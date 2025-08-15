'''
Created on 26 Feb 2021

@author: jacklok
'''
from flask import Blueprint, render_template, request, abort
from trexmodel.utils.model.model_util import create_db_client
from trexmodel.models.datastore.voucher_models import MerchantVoucher
from trexadmin.forms.merchant.voucher_forms import VoucherForm, VoucherBaseForm, VoucherConfigurationForm
from trexadmin.controllers.system.system_route_helpers import get_voucher_status_json,\
    get_voucher_type_json, get_currency_config, get_redeem_limit_type_json
from trexadmin.libs.http import StatusCode, create_rest_message
from trexadmin.libs.flask.decorator.security_decorators import login_required
from trexlib.utils.log_util import get_tracelog
import logging
from trexlib.utils.string_util import is_not_empty, is_empty
from flask.helpers import url_for
from flask_babel import gettext
from trexadmin.libs.flask.utils.flask_helper import get_loggedin_merchant_user_account, get_preferred_language
from trexconf.program_conf import is_voucher_current_status_reach
import trexconf.program_conf as program_conf
from trexlib.utils.google.gcloud_util import connect_to_bucket
from trexlib.utils.common.common_util import sort_list
from trexconf import conf as admin_conf
from flask.json import jsonify
from trexmodel.models.datastore.merchant_models import MerchantAcct,\
    MerchantUser
from trexadmin.controllers.merchant.product.product_category_setup_routes import render_to_select_option_html,\
    get_product_category_structure_code_label_json,\
    get_product_category_code_label_json
from trexadmin.conf import DEFAULT_CURRENCY_CODE
from trexadmin.controllers.merchant.product.product_setup_routes import get_product_code_label_json,\
    get_product_code_group_by_category_label_json
from trexmodel.models.datastore.product_models import Product
from trexlib.libs.flask_wtf.request_wrapper import request_values, with_file,\
    request_form, request_args

voucher_setup_bp = Blueprint('voucher_setup_bp', __name__,
                     template_folder='templates',
                     static_folder='static',
                     url_prefix='/merchant/reward-program/voucher-setup/')


#logger = logging.getLogger('controller')
logger = logging.getLogger('target_debug')


'''
Blueprint settings here
'''
@voucher_setup_bp.context_processor
def voucher_setup_bp_inject_settings():
    
    return dict(
                VOUCHER_STATUS_BASE                 = program_conf.VOUCHER_STATUS_BASE,
                VOUCHER_STATUS_CONFIGURATION        = program_conf.VOUCHER_STATUS_CONFIGURATION,
                VOUCHER_STATUS_UPLOAD_MATERIAL      = program_conf.VOUCHER_STATUS_UPLOAD_MATERIAL,
                VOUCHER_STATUS_PUBLISH              = program_conf.VOUCHER_STATUS_PUBLISH,
                
                VOUCHER_REWARD_TYPE_CASH            = program_conf.VOUCHER_REWARD_TYPE_CASH,
                VOUCHER_REWARD_TYPE_PRODUCT         = program_conf.VOUCHER_REWARD_TYPE_PRODUCT,
                VOUCHER_REWARD_TYPE_DISCOUNT        = program_conf.VOUCHER_REWARD_TYPE_DISCOUNT,
                
                VOUCHER_REWARD_TYPE                 = program_conf.VOUCHER_REWARD_TYPE,
                VOUCHER_REWARD_ACTION_DATA          = program_conf.VOUCHER_REWARD_ACTION_DATA,
                VOUCHER_REWARD_CASH                 = program_conf.VOUCHER_REWARD_CASH,    
                )

def map_label_by_code(code_label_json, code):
    #logger.debug('code_label_json=%s', code_label_json)
    for rb in code_label_json:
        if rb.get('code')==code:
            return rb.get('label')


@voucher_setup_bp.app_template_filter()
def voucher_completed_status_label(voucher_completed_status_code):
    if voucher_completed_status_code:
        preferred_language  = get_preferred_language()
        code_label_json     = get_voucher_status_json(preferred_language)
        return map_label_by_code(code_label_json, voucher_completed_status_code)
    else:
        return ''
    
@voucher_setup_bp.app_template_filter()
def voucher_type_label(voucher_type_code):
    if voucher_type_code:
        preferred_language  = get_preferred_language()
        code_label_json     = get_voucher_type_json(preferred_language)
        return map_label_by_code(code_label_json, voucher_type_code)
    else:
        return ''    

@voucher_setup_bp.app_template_filter()
def redeem_limit_type_label(redeem_limit_type_code):
    if redeem_limit_type_code:
        preferred_language  = get_preferred_language()
        code_label_json     = get_redeem_limit_type_json(preferred_language)
        return map_label_by_code(code_label_json, redeem_limit_type_code)
    else:
        return ''

@voucher_setup_bp.app_template_filter()
def product_category_label(category_code):
    logger.debug('category_code=%s', category_code)
    if category_code:
        code_label_json     = get_product_category_code_label_json()
        return map_label_by_code(code_label_json, category_code)
    else:
        return ''    


@voucher_setup_bp.app_template_filter()
def product_sku_label(product_sku_code):
    logger.debug('product_sku_code=%s', product_sku_code)
    if product_sku_code:
        code_label_json     = get_product_code_label_json()
        return map_label_by_code(code_label_json, product_sku_code)
    else:
        return ''    


@voucher_setup_bp.route('/', methods=['GET'])
@login_required
def voucher_overview():
    return show_voucher_overview('merchant/loyalty/reward_program/voucher_setup/voucher_overview.html' )

@voucher_setup_bp.route('/voucher-listing-content', methods=['GET'])
@login_required
def voucher_overview_content():
    return show_voucher_overview('merchant/loyalty/reward_program/voucher_setup/voucher_overview_content.html', show_page_refresh=False)
    
def show_voucher_overview(template_name, show_page_refresh=True):     
    logger.debug('---voucher_overview---')
    
    logged_in_merchant_user = get_loggedin_merchant_user_account()
    merchant_vouchers_list  = []
    currency_code           = DEFAULT_CURRENCY_CODE
    db_client = create_db_client(caller_info="program_index")
    try:
        if logged_in_merchant_user:
            with db_client.context():
                merchant_acct   = MerchantAcct.get_or_read_from_cache(logged_in_merchant_user.get('merchant_acct_key'))
                currency_code   = merchant_acct.currency_code
                __merchant_vourchers_list   = MerchantVoucher.list_latest_by_merchant_account(merchant_acct)
                __merchant_vourchers_list   = sort_list(__merchant_vourchers_list, sort_attr_name='created_datetime', reverse_order=True)
            
            logger.debug('total voucher count=%d', len(__merchant_vourchers_list))
            
            for mv in __merchant_vourchers_list:
                merchant_vouchers_list.append(mv.to_dict())
    except:
        logger.error('Fail to get merchant voucher due to %s', get_tracelog())
           
    currency_details    = get_currency_config(currency_code)   
    
    return render_template(template_name, 
                           page_title                   = gettext('Voucher Setup'),
                           page_url                     = url_for('voucher_setup_bp.voucher_overview') if show_page_refresh else None,
                           archived_voucher_listing_url = url_for('voucher_setup_bp.archived_voucher_listing'),
                           voucher_listing_reload_url   = url_for('voucher_setup_bp.voucher_overview_content'),
                           merchant_vouchers_list       = merchant_vouchers_list,
                           currency_details             = currency_details,
                           product_sku_list             = get_product_code_label_json(),
                           )
    
@voucher_setup_bp.route('/archived-voucher', methods=['GET'])
@login_required
def archived_voucher_listing(): 
    logger.debug('---archived_voucher_listing---')
    
    logged_in_merchant_user = get_loggedin_merchant_user_account()
    merchant_vouchers_list  = []
    
    db_client = create_db_client(caller_info="archived_voucher_listing")
    try:
        if logged_in_merchant_user:
            with db_client.context():
                merchant_acct   = MerchantAcct.get_or_read_from_cache(logged_in_merchant_user.get('merchant_acct_key'))
                __merchant_vourchers_list   = MerchantVoucher.list_archived_by_merchant_account(merchant_acct)
                __merchant_vourchers_list   = sort_list(__merchant_vourchers_list, sort_attr_name='archived_datetime', reverse_order=True)
            
            for mv in __merchant_vourchers_list:
                merchant_vouchers_list.append(mv.to_dict())
    except:
        logger.error('Fail to get merchant programs due to %s', get_tracelog())
    
    
    logger.debug('merchant_vouchers_list=%s', merchant_vouchers_list)
    
    return render_template('merchant/loyalty/reward_program/voucher_setup/archived_voucher.html',
                           merchant_vouchers_list   = merchant_vouchers_list,
                           show_full = False,
                           )    
    
@voucher_setup_bp.route('/create-voucher', methods=['GET'])
@login_required
def create_voucher(): 
    logger.debug('---create_voucher---')
    currency_code                           = DEFAULT_CURRENCY_CODE
    product_category_structure_option       = get_product_category_structure_code_label_json()
    product_category_select_option_html     = render_to_select_option_html(product_category_structure_option, show_product_item_in_data=True)
    
    currency_details    = get_currency_config(currency_code)
    
    return render_template('merchant/loyalty/reward_program/voucher_setup/create_voucher.html',
                           define_voucher_base                  = url_for('voucher_setup_bp.define_voucher_base_post'),
                           define_voucher_configuration         = url_for('voucher_setup_bp.define_voucher_configuration_post'),
                           upload_voucher_material              = url_for('voucher_setup_bp.upload_voucher_material_post'),
                           publish_voucher                      = url_for('voucher_setup_bp.publish_voucher_post'),
                           show_voucher_review                  = url_for('voucher_setup_bp.show_voucher_review'),
                           update_voucher_material_uploaded     = url_for('voucher_setup_bp.define_voucher_upload_material_post'),
                           voucher_default_image_url            = admin_conf.VOUCHER_DEFAULT_IMAGE,
                           product_category_select_option_html  = product_category_select_option_html,
                           currency_details                     = currency_details,
                           product_sku_group_by_category_list   = get_product_code_group_by_category_label_json(),
                           )    
    
@voucher_setup_bp.route('/edit-voucher/<voucher_key>', methods=['GET'])
@login_required
def edit_voucher(voucher_key): 
    logger.debug('---edit_voucher---')
    voucher                 = None
    currency_code           = DEFAULT_CURRENCY_CODE
    
    if is_not_empty(voucher_key):
        db_client = create_db_client(caller_info="edit_voucher")
            
        try:
            with db_client.context():
                voucher = MerchantVoucher.fetch(voucher_key)
                
            voucher_dict = voucher.to_dict()
            #voucher_dict['image_public_url'] = '/static/app/assets/img/voucher/voucher-sample-image.png'
            
            selected_product_category = None
            
            if voucher.voucher_type == program_conf.VOUCHER_REWARD_TYPE_PRODUCT:
                selected_product_category = voucher.product_category
              
            product_category_structure_option    = get_product_category_structure_code_label_json()
            product_category_select_option_html  = render_to_select_option_html(
                                                    product_category_structure_option,
                                                    selected_category_code = selected_product_category, 
                                                    show_product_item_in_data=True
                                                    )  
            
            currency_details    = get_currency_config(currency_code)
            
            return render_template('merchant/loyalty/reward_program/voucher_setup/create_voucher.html', 
                           define_voucher_base                      = url_for('voucher_setup_bp.define_voucher_base_post'),
                           define_voucher_configuration             = url_for('voucher_setup_bp.define_voucher_configuration_post'),
                           #define_voucher_reward_type_input         = url_for('voucher_setup_bp.define_voucher_reward_type_input'),
                           upload_voucher_material                  = url_for('voucher_setup_bp.upload_voucher_material_post'),
                           publish_voucher                          = url_for('voucher_setup_bp.publish_voucher_post'),
                           show_voucher_review                      = url_for('voucher_setup_bp.show_voucher_review'),
                           update_voucher_material_uploaded         = url_for('voucher_setup_bp.define_voucher_upload_material_post'),
                           
                           VOUCHER_STATUS_BASE_COMPLETED            = True,
                           VOUCHER_STATUS_CONFIGURATION_COMPLETED   = is_voucher_current_status_reach(program_conf.VOUCHER_STATUS_CONFIGURATION, voucher.completed_status),
                           VOUCHER_STATUS_UPLOAD_MATERIAL_COMPLETED = is_voucher_current_status_reach(program_conf.VOUCHER_STATUS_UPLOAD_MATERIAL, voucher.completed_status),
                           VOUCHER_STATUS_PUBLISH_COMPLETED         = is_voucher_current_status_reach(program_conf.VOUCHER_STATUS_PUBLISH, voucher.completed_status),
                           voucher                                  = voucher_dict,
                           voucher_completed_status                 = voucher.completed_status,
                           is_edit_voucher                          = True,
                           product_category_select_option_html      = product_category_select_option_html,
                           product_sku_group_by_category_list       = get_product_code_group_by_category_label_json(),
                           currency_details                         = currency_details,
                           )
                
        except:
            logger.error('Fail to read merchant voucher due to %s', get_tracelog())
            return create_rest_message(gettext('Failed to read merchant voucher'), status_code=StatusCode.BAD_REQUEST)
    else:
        return create_rest_message(gettext('Failed to read merchant voucher'), status_code=StatusCode.BAD_REQUEST)

@voucher_setup_bp.route('/upload-voucher-image', methods=['POST'])    
@request_values
@with_file(field_name='file', max_file_size=1*1024*1024)
def upload_voucher_material_post(request_values, uploaded_file):    
    voucher_key                     = request_values.get('voucher_key')
    #uploaded_file                   = request.files.get('file')
    
    logged_in_merchant_user = get_loggedin_merchant_user_account()
    logger.debug('request_values=%s', request_values)
    logger.debug('voucher_key=%s', voucher_key)
    logger.debug('uploaded_file=%s', uploaded_file)
    
    if not uploaded_file:
        return create_rest_message(status_code=StatusCode.BAD_REQUEST, message=gettext('No file have been uploaded'))
    
    if is_empty(voucher_key):
        return create_rest_message(status_code=StatusCode.BAD_REQUEST, message=gettext('Invalid voucher data'))
    
    db_client       = create_db_client( caller_info="upload_voucher_material_post")
    voucher         = None
    
    with db_client.context():
        merchant_user   = MerchantUser.get_by_user_id(logged_in_merchant_user.get('user_id'))
        merchant_acct   = MerchantAcct.get_or_read_from_cache(logged_in_merchant_user.get('merchant_acct_key'))
        if merchant_acct:
            merchant_acct_key       = merchant_acct.key_in_str
            voucher                 = MerchantVoucher.fetch(voucher_key)
            bucket                  = connect_to_bucket(credential_filepath=admin_conf.STORAGE_CREDENTIAL_PATH)    
            image_storage_filename  = 'merchant/'+merchant_acct_key+'/voucher/'+uploaded_file.filename
            blob                    = bucket.blob(image_storage_filename)
            
            blob.upload_from_string(
                uploaded_file.read(),
                content_type=uploaded_file.content_type
            )
        
            uploaded_url        = blob.public_url
            
            if is_not_empty(voucher.image_public_url):
                old_logo_blob = bucket.get_blob(voucher.image_public_url) 
                if old_logo_blob:
                    old_logo_blob.delete()

            voucher.image_public_url       = uploaded_url
            voucher.image_storage_filename = image_storage_filename
            
            MerchantVoucher.update_voucher_material(voucher, 
                                                    image_public_url        = uploaded_url, 
                                                    image_storage_filename  = image_storage_filename, 
                                                    modified_by             = merchant_user
                                                    )
            
            logger.debug('After uploaded voucher image url')
            
        else:
            logger.warn('Failed to fetch voucher data')
         
    if merchant_acct is None or voucher is None:
        return create_rest_message(status_code=StatusCode.BAD_REQUEST, message=gettext('Invalid voucher data'))    
            
    
    return create_rest_message(status_code=StatusCode.OK, uploaded_url=uploaded_url)  
    
@voucher_setup_bp.route('/view-voucher/<voucher_key>', methods=['GET'])
@login_required
def view_voucher(voucher_key): 
    logger.debug('---view_voucher---')
    voucher = None
    currency_code           = DEFAULT_CURRENCY_CODE
    if is_not_empty(voucher_key):
        db_client = create_db_client(caller_info="view_program")
            
        try:
            with db_client.context():
                voucher = MerchantVoucher.fetch(voucher_key)
            
            currency_details    = get_currency_config(currency_code)
            product_category_structure_option       = get_product_category_structure_code_label_json()
            product_category_select_option_html     = render_to_select_option_html(product_category_structure_option, show_product_item_in_data=True)
            
            return render_template('merchant/loyalty/reward_program/voucher_setup/view_voucher.html',
                                   
                           is_view_voucher                          = True,
                           voucher_default_image_url                = admin_conf.VOUCHER_DEFAULT_IMAGE,
                           upload_voucher_material                  = url_for('voucher_setup_bp.upload_voucher_material_post'),
                           voucher                                  = voucher.to_dict(),
                           currency_details                         = currency_details,
                           voucher_completed_status                 = voucher.completed_status,
                           product_category_select_option_html      = product_category_select_option_html,
                           product_sku_group_by_category_list       = get_product_code_group_by_category_label_json(),
                           )
                
        except:
            logger.error('Fail to view merchant voucher due to %s', get_tracelog())
            return create_rest_message(gettext('Failed to view merchant voucher'), status_code=StatusCode.BAD_REQUEST)
    else:
        return create_rest_message(gettext('Failed to view merchant voucher'), status_code=StatusCode.BAD_REQUEST)    


@voucher_setup_bp.route('/define-voucher-base', methods=['POST'])
@login_required
@request_form
def define_voucher_base_post(request_form): 
    logger.debug('---define_voucher_base_post---')
    
    voucher_base_data = request_form
    voucher_base_form = VoucherBaseForm(voucher_base_data)
    
    logger.debug('voucher_base_form=%s', voucher_base_form)
    
    logged_in_merchant_user = get_loggedin_merchant_user_account()
    
    voucher_key = voucher_base_form.voucher_key.data
    
    logger.debug('voucher_key=%s', voucher_key)
    
    if logged_in_merchant_user is None:
        raise abort(401)
    
    if voucher_base_form.validate():
    
        db_client               = create_db_client(caller_info="define_voucher_base_post")
        
        try:
            with db_client.context():
                merchant_user   = MerchantUser.get_by_user_id(logged_in_merchant_user.get('user_id'))
                merchant_acct   = MerchantAcct.get_or_read_from_cache(logged_in_merchant_user.get('merchant_acct_key'))
                
                if is_empty(voucher_key):
                    
                    voucher             = MerchantVoucher.create(merchant_acct, 
                                                             label                  = voucher_base_form.voucher_label.data,
                                                             voucher_type           = voucher_base_form.voucher_type.data,
                                                             desc                   = voucher_base_form.desc.data,
                                                             terms_and_conditions   = voucher_base_form.terms_and_conditions.data,
                                                             redeem_limit_type      = voucher_base_form.redeem_limit_type.data,
                                                             redeem_limit_count     = voucher_base_form.redeem_limit_count.data,
                                                             created_by             = merchant_user,
                                                             voucher_image_url      = admin_conf.VOUCHER_DEFAULT_IMAGE,
                                                             )
                    
                    voucher_key      = voucher.key_in_str
                    
                else:
                    
                    voucher = MerchantVoucher.fetch(voucher_key)
                    if voucher:
                        MerchantVoucher.update_voucher_base_data(voucher, 
                                                                  label                  = voucher_base_form.voucher_label.data,
                                                                  voucher_type           = voucher_base_form.voucher_type.data,   
                                                                  desc                   = voucher_base_form.desc.data,
                                                                  terms_and_conditions   = voucher_base_form.terms_and_conditions.data,
                                                                  redeem_limit_type      = voucher_base_form.redeem_limit_type.data,
                                                                  redeem_limit_count     = voucher_base_form.redeem_limit_count.data,
                                                                  modified_by            = merchant_user
                                                                  )
                logger.debug('voucher=%s', voucher)
            
            if voucher is None:
                return create_rest_message(gettext('Invalid merchant voucher'), status_code=StatusCode.BAD_REQUEST)
            
        except:
            logger.error('Fail to create merchant voucher due to %s', get_tracelog())
            return create_rest_message(gettext('Failed to update merchant voucher'), status_code=StatusCode.BAD_REQUEST)
        
        return create_rest_message(status_code=StatusCode.OK, 
                                    voucher_key                             = voucher_key,
                                    )
        
    else:
        error_message = voucher_base_form.create_rest_return_error_message()
        logger.warn('Failed due to form validation where %s', error_message)
            
        return create_rest_message(error_message, status_code=StatusCode.BAD_REQUEST)
    
@voucher_setup_bp.route('/define-voucher-upload-material', methods=['POST'])
@login_required
@request_form
def define_voucher_upload_material_post(request_form): 
    logger.debug('---define_voucher_upload_material_post---')
    
    voucher_data = request_form
    voucher_form = VoucherForm(voucher_data)
    
    logger.debug('voucher_form=%s', voucher_form)
    
    logged_in_merchant_user = get_loggedin_merchant_user_account()
    
    voucher_key = voucher_form.voucher_key.data
    
    logger.debug('voucher_key=%s', voucher_key)
    
    if logged_in_merchant_user is None:
        raise abort(401)
    
    if voucher_form.validate():
    
        db_client               = create_db_client(caller_info="define_voucher_upload_material_post")
        
        try:
            with db_client.context():
                voucher = MerchantVoucher.fetch(voucher_key)
                if voucher:
                    merchant_user   = MerchantUser.get_by_user_id(logged_in_merchant_user.get('user_id'))
                    MerchantVoucher.update_voucher_material_uploaded(voucher, 
                                                         modified_by    = merchant_user
                                                         )
            
            if voucher is None:
                return create_rest_message(gettext('Invalid merchant voucher data'), status_code=StatusCode.BAD_REQUEST)
            
        except:
            logger.error('Fail to update merchant voucher due to %s', get_tracelog())
            return create_rest_message(gettext('Failed to update merchant voucher'), status_code=StatusCode.BAD_REQUEST)
        
        return create_rest_message(status_code=StatusCode.OK, 
                                    voucher_key                             = voucher_key,
                                    )
        
    else:
        error_message = voucher_form.create_rest_return_error_message()
        logger.warn('Failed due to form validation where %s', error_message)
            
        return create_rest_message(error_message, status_code=StatusCode.BAD_REQUEST)  
    
@voucher_setup_bp.route('/define-voucher-configuration', methods=['POST'])
@login_required
@request_form
def define_voucher_configuration_post(request_form): 
    logger.debug('---define_voucher_configuration_post---')
    
    voucher_configuration_data = request_form
    voucher_configuration_form = VoucherConfigurationForm(voucher_configuration_data)
    
    logger.debug('voucher_configuration_data=%s', voucher_configuration_data)
    
    logged_in_merchant_user = get_loggedin_merchant_user_account()
    
    voucher_key     = voucher_configuration_form.voucher_key.data
    voucher_type    = voucher_configuration_form.voucher_type.data
    
    logger.debug('voucher_key=%s', voucher_key)
    logger.debug('voucher_type=%s', voucher_type)
    
    
    if logged_in_merchant_user is None:
        raise abort(401)
    
    if voucher_configuration_form.validate():
        voucher_conf_in_json    = {}
        min_sales_amount        = voucher_configuration_form.min_sales_amount.data
        
        db_client  = create_db_client(caller_info="define_voucher_configuration_post")
        
        with db_client.context():
            voucher = MerchantVoucher.fetch(voucher_key)
            merchant_acct = voucher.merchant_acct
            
        if voucher:
        
            if voucher_type == program_conf.VOUCHER_REWARD_TYPE_CASH:
                cash_amount             = voucher_configuration_form.cash_amount.data
                
                voucher_conf_in_json    = MerchantVoucher.construct_cash_voucher_configuration(cash_amount, 
                                                                                               min_sales_amount=min_sales_amount)
                    
                
            elif voucher_type == program_conf.VOUCHER_REWARD_TYPE_DISCOUNT:
                discount_rate           = voucher_configuration_form.discount_rate.data
                voucher_conf_in_json    = MerchantVoucher.construct_discount_voucher_configuration(discount_rate, 
                                                                                                   min_sales_amount=min_sales_amount)
                
            elif voucher_type == program_conf.VOUCHER_REWARD_TYPE_PRODUCT:
                product_category        = voucher_configuration_form.product_category.data
                product_sku             = voucher_configuration_form.product_sku.data
                product_price           = voucher_configuration_form.product_price.data
                
                with db_client.context():
                    product = Product.get_by_product_sku(product_sku, merchant_acct)
                
                voucher_conf_in_json    = MerchantVoucher.construct_product_voucher_configuration(product_sku, 
                                                                                                  category=product_category, 
                                                                                                  price=product_price, 
                                                                                                  min_sales_amount=min_sales_amount)
                
                voucher_conf_in_json['image_public_url']    = product.product_default_image
                
            logger.debug('voucher_conf_in_json=%s', voucher_conf_in_json)
            
            voucher_conf_in_json['redeem_limit_type']   = voucher.redeem_limit_type
            voucher_conf_in_json['redeem_limit_count']  = voucher.redeem_limit_count
            
            
            try:
                with db_client.context():
                    
                    merchant_user   = MerchantUser.get_by_user_id(logged_in_merchant_user.get('user_id'))
                    
                    MerchantVoucher.update_voucher_configuration_data(voucher, 
                                                         configuration      = voucher_conf_in_json,
                                                         modified_by        = merchant_user,
                                                         image_public_url   = voucher_conf_in_json.get('image_public_url'),
                                                         )
                
                
            except:
                logger.error('Fail to update merchant voucher due to %s', get_tracelog())
                return create_rest_message(gettext('Failed to update merchant voucher'), status_code=StatusCode.BAD_REQUEST)
            
            return create_rest_message(status_code=StatusCode.OK, 
                                        voucher_key                             = voucher_key,
                                        )
        else:
            return create_rest_message(gettext('Invalid merchant voucher data'), status_code=StatusCode.BAD_REQUEST)
            
         
        
        
    else:
        error_message = voucher_configuration_form.create_rest_return_error_message()
        logger.warn('Failed due to form validation where %s', error_message)
            
        return create_rest_message(error_message, status_code=StatusCode.BAD_REQUEST) 

@voucher_setup_bp.route('/archive-voucher', methods=['POST','GET'])
@login_required
@request_args
def archive_voucher_post(request_args): 
    
    logger.debug('---archive_voucher_post---')
    
    voucher_key = request_args.get('voucher_key')
    
    logger.debug('voucher_key=%s', voucher_key)
    
    db_client               = create_db_client(caller_info="archive_program_post")
    try:
        with db_client.context():
            if is_empty(voucher_key):
                return create_rest_message(gettext('Invaid voucher data'), status_code=StatusCode.BAD_REQUEST)
                
            else:
                
                voucher = MerchantVoucher.fetch(voucher_key)
                if voucher:
                    MerchantVoucher.archive_voucher(voucher)
                    
        if voucher is None:
            return create_rest_message(gettext('Invalid merchant voucher'), status_code=StatusCode.BAD_REQUEST)
        
            
    except:
        logger.error('Fail to archive merchant voucher due to %s', get_tracelog())
        return create_rest_message(gettext('Failed to archive merchant voucher'), status_code=StatusCode.BAD_REQUEST)
        
    return create_rest_message(status_code=StatusCode.OK,) 

@voucher_setup_bp.route('/disable-voucher', methods=['POST','GET'])
@login_required
@request_args
def disable_voucher_post(request_args): 
    
    logger.debug('---disable_voucher_post---')
    
    voucher_key = request_args.get('voucher_key')
    
    logger.debug('voucher_key=%s', voucher_key)
    
    db_client               = create_db_client(caller_info="disable_voucher_post")
    try:
        with db_client.context():
            if is_empty(voucher_key):
                return create_rest_message(gettext('Invaid voucher data'), status_code=StatusCode.BAD_REQUEST)
                
            else:
                
                voucher = MerchantVoucher.fetch(voucher_key)
                if voucher:
                    logger.info('going to disable voucher')
                    MerchantVoucher.disable_voucher(voucher)
                    
        if voucher is None:
            return create_rest_message(gettext('Invalid merchant voucher'), status_code=StatusCode.BAD_REQUEST)
        
            
    except:
        logger.error('Fail to disable merchant voucher due to %s', get_tracelog())
        return create_rest_message(gettext('Failed to disable merchant voucher'), status_code=StatusCode.BAD_REQUEST)
        
    return create_rest_message(status_code=StatusCode.OK,) 

@voucher_setup_bp.route('/enable-voucher', methods=['POST','GET'])
@login_required
@request_args
def enable_voucher_post(request_args): 
    
    logger.debug('---enable_voucher_post---')
    
    voucher_key = request_args.get('voucher_key')
    
    logger.debug('voucher_key=%s', voucher_key)
    
    db_client               = create_db_client(caller_info="enable_voucher_post")
    try:
        with db_client.context():
            if is_empty(voucher_key):
                return create_rest_message(gettext('Invaid voucher data'), status_code=StatusCode.BAD_REQUEST)
                
            else:
                
                voucher = MerchantVoucher.fetch(voucher_key)
                if voucher:
                    logger.info('going to enable voucher')
                    MerchantVoucher.enable_voucher(voucher)
                    
        if voucher is None:
            return create_rest_message(gettext('Invalid merchant voucher'), status_code=StatusCode.BAD_REQUEST)
        
            
    except:
        logger.error('Fail to enable merchant voucher due to %s', get_tracelog())
        return create_rest_message(gettext('Failed to enable merchant voucher'), status_code=StatusCode.BAD_REQUEST)
        
    return create_rest_message(status_code=StatusCode.OK,)  

@voucher_setup_bp.route('/publlish-voucher', methods=['POST','GET'])
@login_required
@request_values
def publish_voucher_post(request_values): 
    
    logger.debug('---publish_voucher_post---')
    
    logged_in_merchant_user = get_loggedin_merchant_user_account()
    if logged_in_merchant_user is None:
        raise abort(401)
    
    voucher_key = request_values.get('voucher_key')
    
    logger.debug('voucher_key=%s', voucher_key)
    
    db_client               = create_db_client(caller_info="publish_voucher_post")
    try:
        with db_client.context():
            if is_empty(voucher_key):
                return create_rest_message(gettext('Invaid voucher data'), status_code=StatusCode.BAD_REQUEST)
                
            else:
                
                voucher = MerchantVoucher.fetch(voucher_key)
                if voucher:
                    MerchantVoucher.publish_voucher(voucher)
                    
        if voucher is None:
            return create_rest_message(gettext('Invalid merchant voucher'), status_code=StatusCode.BAD_REQUEST)
        
            
    except:
        logger.error('Fail to publish merchant voucher due to %s', get_tracelog())
        return create_rest_message(gettext('Failed to publish merchant voucher'), status_code=StatusCode.BAD_REQUEST)
        
    return create_rest_message(status_code=StatusCode.OK,)   

@voucher_setup_bp.route('/show-voucher-review', methods=['GET'])
@login_required
def show_voucher_review(): 
    logger.debug('---show_voucher_review---')
    
    voucher_key = request.args.get('voucher_key')
    
    db_client = create_db_client(caller_info="show_voucher_review")
    try:
        
        with db_client.context():
            voucher = MerchantVoucher.fetch(voucher_key)
            
            
    except:
        logger.error('Fail to get voucher setup due to %s', get_tracelog())
           
    
    voucher_dict = voucher.to_dict()
    
    return render_template('merchant/loyalty/reward_program/voucher_setup/voucher_review_content.html', 
                           voucher   = voucher_dict,
                           )
    
@voucher_setup_bp.route('/show-voucher-details', methods=['GET'])
@login_required
def show_voucher_details(): 
    logger.debug('---show_voucher_review---')
    
    voucher_key = request.args.get('voucher_key')
    
    db_client = create_db_client(caller_info="show_voucher_review")
    try:
        
        with db_client.context():
            voucher = MerchantVoucher.fetch(voucher_key)
            
            
    except:
        logger.error('Fail to get merchant programs due to %s', get_tracelog())
           
    
    voucher_dict = voucher.to_dict()
    
    return jsonify(voucher_dict)    
    
