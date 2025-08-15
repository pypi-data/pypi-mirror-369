'''
Created on 22 Dec 2020

@author: jacklok
'''
from flask import Blueprint, render_template
from trexmodel.utils.model.model_util import create_db_client
from trexadmin.libs.http import StatusCode, create_rest_message
from trexadmin.libs.flask.pagination import CursorPager
from trexadmin.libs.flask.decorator.security_decorators import login_required, login_required_rest
from trexlib.utils.common.pagination_util import get_offset_by_page_no
from trexlib.utils.log_util import get_tracelog
import logging
from trexmodel.models.datastore.merchant_models import MerchantAcct, Outlet
from trexlib.utils.string_util import is_not_empty, is_empty
from trexadmin.forms.merchant.merchant_forms import AddMerchantOutletForm, MerchantOutletDetailsForm,\
    SearchMerchantOutletForm
from flask.helpers import url_for
from flask_babel import gettext
from trexadmin.libs.flask.utils.flask_helper import get_loggedin_merchant_user_account
from google.cloud.ndb.model import GeoPt
from trexconf.conf import PAGINATION_SIZE
from trexlib.libs.flask_wtf.request_wrapper import request_args, request_form,\
    request_values
from werkzeug.datastructures import ImmutableMultiDict

merchant_manage_outlet_bp = Blueprint('merchant_manage_outlet_bp', __name__,
                     template_folder='templates',
                     static_folder='static',
                     url_prefix='/merchant/manage-outlet')


#logger = logging.getLogger('controller')
logger = logging.getLogger('target_debug')

'''
Blueprint settings here
'''
@merchant_manage_outlet_bp.context_processor
def manage_customer_bp_inject_settings():
    
    return dict(
                side_menu_group_name    = "merchant",
                
                )

@merchant_manage_outlet_bp.route('/', methods=['GET'])
@login_required
def manage_outlet(): 
    logger.debug('---manage_outlet---')
    
    logged_in_merchant_user = get_loggedin_merchant_user_account()
    
    db_client       = create_db_client(caller_info="list_user")
    
    with db_client.context():
        merchant_acct_key = logged_in_merchant_user.get('merchant_acct_key')
        merchant_acct   = MerchantAcct.fetch(merchant_acct_key)
        outlet_limit    = merchant_acct.outlet_limit
        outlet_count    = merchant_acct.outlet_count
        remaining_limit = outlet_limit- outlet_count
        is_reach_outlet_max_count = outlet_count>=outlet_limit
        
    return render_template('merchant/settings/manage_outlet/manage_outlet_index.html', 
                           page_title                           = gettext('Manage Outlet'),
                           page_url                             = url_for('merchant_manage_outlet_bp.manage_outlet'),
                           merchant_acct_key                    = merchant_acct_key,
                           list_all_outlet_url                  = url_for('merchant_manage_outlet_bp.list_outlet_by_page', limit=PAGINATION_SIZE, page_no=1),
                           add_outlet_url                       = url_for('merchant_manage_outlet_bp.add_outlet'),
                           search_outlet_url                    = url_for('merchant_manage_outlet_bp.search_outlet', limit=PAGINATION_SIZE, page_no=1),
                           outlet_count                         = outlet_count,
                           outlet_limit                         = outlet_limit,
                           is_reach_outlet_max_count            = is_reach_outlet_max_count,
                           remaining_limit                      = remaining_limit,
                           reach_limit                          = remaining_limit<=0,
                           )

def list_outlet_function(merchant_acct_key, template_path, outlet_list,
                           add_merchant_outlet_url              = None,
                           edit_merchant_outlet_url              = None,
                           delete_merchant_outlet_url           = None,
                           pager                                = None,
                           pages                                = None,
                           end_point                            = None,
                           pagination_target_selector           = '#outlet_list_div',
                           
                           ):    
    
    if edit_merchant_outlet_url is None:
        edit_merchant_outlet_url           = 'merchant_manage_outlet_bp.read_outlet'
    
    if delete_merchant_outlet_url is None:
        delete_merchant_outlet_url         = 'merchant_manage_outlet_bp.delete_outlet'
    
    return render_template(template_path,
                           merchant_acct_key                    = merchant_acct_key,
                           outlet_list                          = outlet_list,
                           add_merchant_outlet_url_path         = add_merchant_outlet_url,
                           edit_merchant_outlet_url_path        = edit_merchant_outlet_url,
                           delete_merchant_outlet_url_path      = delete_merchant_outlet_url,
                           pager                                = pager,
                           pages                                = pages,
                           end_point                            = end_point,
                           pagination_target_selector           = pagination_target_selector,
                           skip_for_partial_content_js_loading  = True
                           )
    
@merchant_manage_outlet_bp.route('/list-outlet/all/page-size/<limit>/page/<page_no>', methods=['GET'])
@login_required
@request_args
def list_outlet_by_page(request_args, limit, page_no): 
    logger.debug('---manage_outlet---')
    
    logged_in_merchant_user = get_loggedin_merchant_user_account()
    
    merchant_outlet_list = []
    
    logger.debug('page_no=%s', page_no)
    
    page_no_int = int(page_no, 10)
    
    template_path = 'merchant/settings/manage_outlet/merchant_outlet_listing.html'
    
    
    offset          = get_offset_by_page_no(page_no, limit=limit)
    limit_int       = int(limit, 10)
    
    db_client = create_db_client(caller_info="list_all_outlet")
    
    cursor                          = request_args.get('cursor')
    previous_cursor                 = request_args.get('previous_cursor')
    
    logger.debug('offset=%s', offset)
    logger.debug('cursor=%s', cursor)
    logger.debug('previous_cursor=%s', previous_cursor)
    
    with db_client.context():
        merchant_acct   = MerchantAcct.fetch(logged_in_merchant_user.get('merchant_acct_key'))
        total_count             = Outlet.count_by_merchant_account(merchant_acct)
        (result, next_cursor)   = Outlet.list_all_by_merchant_account(merchant_acct, 
                                                                        offset              = offset,
                                                                        limit               = limit_int,
                                                                        start_cursor        = cursor, 
                                                                        return_with_cursor  = True,
                                                                        )
        
        
        if result:
            for m in result:
                merchant_outlet_list.append(m.to_dict())
    
    pager       = CursorPager(page_no_int, total_count, limit_int, 
                                        next_cursor                     = next_cursor, 
                                        previous_cursor                 = previous_cursor,
                                        current_cursor                  = cursor,
                                      )
    
    pages       = pager.get_pages()
    
    return list_outlet_function(logged_in_merchant_user.get('merchant_acct_key'), template_path, merchant_outlet_list,
                              pager     = pager,
                              pages     = pages,
                              end_point = 'merchant_manage_outlet_bp.list_outlet_by_page',
                              )
    
@merchant_manage_outlet_bp.route('/search/page-size/<limit>/page/<page_no>', methods=['POST'])
@login_required_rest
@request_values
@request_args
def search_outlet(request_values, request_args, limit, page_no):
 
    logger.debug('---search_outlet---')
    
    logger.debug('search_outlet_data=%s', request_values)
    
    search_outlet_form = SearchMerchantOutletForm(ImmutableMultiDict(request_values))
    
    
    page_no_int = int(page_no, 10)
    
    template_path = 'merchant/settings/manage_outlet/merchant_outlet_listing.html'
    
    
    limit_int       = int(limit, 10)
    
    cursor                          = request_args.get('cursor')
    previous_cursor                 = request_args.get('previous_cursor')
    merchant_outlet_list            = []
    
    logger.debug('cursor=%s', cursor)
    logger.debug('previous_cursor=%s', previous_cursor)
    
    
    logger.debug('limit_int=%s', limit_int)
    
    logged_in_merchant_user = get_loggedin_merchant_user_account()
    
    try:
        if search_outlet_form.validate():
            db_client = create_db_client(caller_info="search_user")
            with db_client.context():
                (result, total_count, next_cursor) = Outlet.search_by_merchant_account(
                                                            name        = search_outlet_form.name.data,
                                                            limit       = limit_int
                                                            )
                
                logger.debug('total_count=%s', total_count)
                
                if result:
                    for m in result:
                        merchant_outlet_list.append(m.to_dict())
            
            pager       = CursorPager(page_no_int, total_count, limit_int, 
                                        next_cursor                     = next_cursor, 
                                        previous_cursor                 = previous_cursor,
                                        current_cursor                  = cursor,
                                      )
            
            pages       = pager.get_pages()
            
            return list_outlet_function(logged_in_merchant_user.get('merchant_acct_key'), template_path, merchant_outlet_list,
                              pager     = pager,
                              pages     = pages,
                              end_point = 'merchant_manage_outlet_bp.list_outlet_by_page',
                              )
            
        else:
            error_message = search_outlet_form.create_rest_return_error_message()
            
            return create_rest_message(error_message, status_code=StatusCode.BAD_REQUEST)
        
    except:
        logger.error('Fail to search user due to %s', get_tracelog())
        return create_rest_message(gettext('Failed to search outlet'), status_code=StatusCode.BAD_REQUEST)        


@merchant_manage_outlet_bp.route('/add', methods=['GET'])
@login_required
def add_outlet():
    
    logged_in_merchant_user = get_loggedin_merchant_user_account()
    
    logger.debug('list_user: logged_in_merchant_user=%s', logged_in_merchant_user)
     
    return render_template('merchant/settings/manage_outlet/manage_outlet_details.html',
                           show_password_input  = True,
                           page_title           = gettext('Add Outlet'),
                           merchant_acct_key    = logged_in_merchant_user.get('merchant_acct_key'),
                           post_url             = url_for('merchant_manage_outlet_bp.add_outlet_post'),
                           merchant_outlet      = None,
                           )

@merchant_manage_outlet_bp.route('/add', methods=['POST'])
@login_required_rest
@request_form
def add_outlet_post(request_form):
    logged_in_merchant_user = get_loggedin_merchant_user_account()
    
    return add_outlet_post_function(request_form, logged_in_merchant_user.get('merchant_acct_key'), post_url=url_for('merchant_manage_outlet_bp.update_outlet_post'))

    
def add_outlet_post_function(request_form, merchant_acct_key, post_url=None): 
    logger.debug('--- submit add_outlet_post_function ---')
    add_outlet_data = request_form
    
    logger.debug('add_outlet_data=%s', add_outlet_data)
    
    add_outlet_form = AddMerchantOutletForm(add_outlet_data)
    
    try:
        if add_outlet_form.validate():
            
            db_client = create_db_client(caller_info="add_outlet_post_function")
            error_message = None
            with db_client.context():
                try:
                    
                    logger.debug('merchant_acct_key=%s', merchant_acct_key)
                    
                    merchant_acct       = MerchantAcct.fetch(merchant_acct_key)
                    if merchant_acct:
                        
                        geo_location = add_outlet_form.geo_location.data
                        if is_empty(geo_location):
                            geo_location = None
                        else:
                            geo_location_array = geo_location.split(',')
                            geo_location = GeoPt(float(geo_location_array[0]), float(geo_location_array[1]))
                        
                        outlet = Outlet.create(
                                            merchant_acct       = merchant_acct,
                                            name                = add_outlet_form.outlet_name.data,
                                            id                  = add_outlet_form.outlet_id.data,
                                            company_name        = add_outlet_form.company_name.data,
                                            business_reg_no     = add_outlet_form.business_reg_no.data,
                                            address             = add_outlet_form.address.data,
                                            business_hour       = add_outlet_form.business_hour.data,
                                            fax_phone           = add_outlet_form.fax_phone.data,
                                            office_phone        = add_outlet_form.office_phone.data,
                                            email               = add_outlet_form.email.data,
                                            geo_location        = geo_location,
                                            is_physical_store   = add_outlet_form.is_physical_store.data,
                                            is_headquarter      = add_outlet_form.is_headquarter.data,
                                            )
                        
                        
                        
                except:
                    logger.error('Failed to add merchant outlet due to %s', get_tracelog())
                    error_message = gettext('Failed to add merchant outlet')
                    
                
            if error_message:
                return create_rest_message(message = error_message, status_code=StatusCode.BAD_REQUEST)
            else:
                if merchant_acct is None:
                    return create_rest_message(status_code=StatusCode.BAD_REQUEST, message=gettext('Invalid merchant account data'))
                else:
                    return create_rest_message(gettext('Merchant outlet have been created'), 
                                                   status_code=StatusCode.OK, 
                                                   created_merchant_outlet_key = outlet.key_in_str,
                                                   post_url = post_url)
                
            return create_rest_message(status_code=StatusCode.BAD_REQUEST)
        else:
            
            error_message = add_outlet_form.create_rest_return_error_message()
            logger.warn('Failed due to form validation where %s', error_message)
            
            return create_rest_message(error_message, status_code=StatusCode.BAD_REQUEST)
    except:
        logger.error('Fail to register merchant outlet due to %s', get_tracelog())
        
        return create_rest_message(status_code=StatusCode.BAD_REQUEST)
    
@merchant_manage_outlet_bp.route('/update', methods=['post'])
@login_required_rest
@request_form
def update_outlet_post(request_form):
    return update_outlet_post_function(request_form)

def update_outlet_post_function(request_form):    
    logger.debug('--- submit update_outlet_post data ---')
    outlet_details_data = request_form
    
    logger.debug('outlet_details_data=%s', outlet_details_data)
    
    outlet_details_form = MerchantOutletDetailsForm(outlet_details_data)
    outlet_key = outlet_details_form.merchant_outlet_key.data
    
    logger.debug('outlet_details_form=%s', outlet_details_form)
    
    try:
        if is_not_empty(outlet_key):
            if outlet_details_form.validate():
                
                    
                db_client = create_db_client(caller_info="update_outlet_post_function")
                
                with db_client.context():   
                    outlet = Outlet.fetch(outlet_key)
                    logger.debug('outlet=%s', outlet)
                    if outlet:
                        
                        geo_location = outlet_details_form.geo_location.data
                        if is_empty(geo_location):
                            geo_location = None
                        else:
                            geo_location_array = geo_location.split(',')
                            geo_location = GeoPt(float(geo_location_array[0]), float(geo_location_array[1]))
                        
                        logger.debug('is_headquarter=%s', outlet_details_form.is_headquarter.data)
                        logger.debug('is_physical_store=%s', outlet_details_form.is_physical_store.data)
                        
                        Outlet.update(outlet,
                                        name                 = outlet_details_form.outlet_name.data,
                                        id                   = outlet_details_form.outlet_id.data,
                                        company_name         = outlet_details_form.company_name.data,
                                        business_reg_no      = outlet_details_form.business_reg_no.data,
                                        email                = outlet_details_form.email.data,
                                        address              = outlet_details_form.address.data,
                                        office_phone         = outlet_details_form.office_phone.data,
                                        fax_phone            = outlet_details_form.fax_phone.data,
                                        business_hour        = outlet_details_form.business_hour.data,
                                        geo_location         = geo_location,
                                        is_physical_store    = outlet_details_form.is_physical_store.data,
                                        is_headquarter       = outlet_details_form.is_headquarter.data,
                                        )
                        
                
                
                return create_rest_message(gettext('Outlet details have been updated'), status_code=StatusCode.OK)
                    
                    
                return create_rest_message(status_code=StatusCode.BAD_REQUEST)
            else:
                error_message = outlet_details_form.create_rest_return_error_message()
                
                return create_rest_message(error_message, status_code=StatusCode.BAD_REQUEST)
        else:
            return create_rest_message(gettext("Incomplete outlet data"), status_code=StatusCode.BAD_REQUEST)
            
    except Exception as error:
        logger.error('Fail to update outlet due to %s', get_tracelog())
        
        return create_rest_message(message=str(error), status_code=StatusCode.BAD_REQUEST)    

@merchant_manage_outlet_bp.route('/outlet/<outlet_key>', methods=['GET'])
@login_required
def read_outlet(outlet_key):
    return read_outlet_function(outlet_key)
    
def read_outlet_function(outlet_key):     
    logger.debug('---read_outlet---')
    
    logger.debug('outlet_key=%s', outlet_key)
    
    if is_not_empty(outlet_key):
        try:
            
            outlet = None    
                
            db_client = create_db_client(caller_info="read_outlet_function")
            
            with db_client.context():
                outlet = Outlet.fetch(outlet_key)
            
            outlet_dict = outlet.to_dict()
            
            logger.debug('outlet_dict=%s', outlet_dict)
            
            return render_template('merchant/settings/manage_outlet/manage_outlet_details.html', 
                                   page_title       = gettext('Outlet Details'),
                                   post_url         = url_for('merchant_manage_outlet_bp.update_outlet_post'), 
                                   merchant_outlet  = outlet_dict,
                                   show_full        = False,
                                   ) 
                
        except:
            logger.error('Fail to read merchant account details due to %s', get_tracelog())
            
            return create_rest_message(status_code=StatusCode.BAD_REQUEST)
    else:
        return create_rest_message(status_code=StatusCode.BAD_REQUEST)  
    
@merchant_manage_outlet_bp.route('/outlet/<outlet_key>', methods=['delete'])
@login_required_rest
def delete_outlet(outlet_key):
    return delete_outlet_function(outlet_key)
    
def delete_outlet_function(outlet_key):
    
    logger.debug('--- submit delete_outlet data ---')
    try:
        if is_not_empty(outlet_key):
            db_client = create_db_client(caller_info="delete_outlet_function")
            with db_client.context():   
                outlet = Outlet.fetch(outlet_key)
                logger.debug('outlet=%s', outlet)
                if outlet:
                    outlet.key.delete()
            
            return create_rest_message(gettext('Outlet have been deleted'), status_code=StatusCode.OK)
        else:
            return create_rest_message(gettext("Incomplete outlet data"), status_code=StatusCode.BAD_REQUEST)
            
    except:
        logger.error('Fail to delete outlet due to %s', get_tracelog())
        
        return create_rest_message(status_code=StatusCode.BAD_REQUEST)    
    
    