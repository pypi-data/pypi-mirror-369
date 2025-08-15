'''
Created on 30 Aug 2020

@author: jacklok
'''
from flask import Blueprint, render_template
from trexmodel.utils.model.model_util import create_db_client
from trexadmin.libs.http import StatusCode, create_rest_message
from trexadmin.libs.flask.pagination import Pager
from trexadmin.libs.flask.decorator.security_decorators import login_required
from trexlib.utils.common.pagination_util import get_offset_by_page_no
from trexlib.utils.log_util import get_tracelog
import logging
from trexmodel.models.datastore.system_models import ContactUs
from trexlib.utils.string_util import is_not_empty
from flask.helpers import url_for
from flask_babel import gettext
from trexadmin.conf import PAGINATION_SIZE

manage_contact_us_bp = Blueprint('manage_contact_us_bp', __name__,
                     template_folder='templates',
                     static_folder='static',
                     url_prefix='/admin/manage-contact-us')


logger = logging.getLogger('application:manage_contact_us_bp')

'''
Blueprint settings here
'''
@manage_contact_us_bp.context_processor
def manage_contact_us_bp_inject_settings():
    
    return dict(
                side_menu_group_name    = "admin",
                
                )
    
@manage_contact_us_bp.route('/idex', methods=['GET'])
@login_required
def manage_contact_us_listing(): 
    logging.debug('---manage_contact_us_listing---')
    
    page_no_int         = 1
    
    offset              = 0
    total_count         = 0
    contact_us_list     = []
    limit_int           = PAGINATION_SIZE
    
    db_client = create_db_client(caller_info="list_merchant")
        
    with db_client.context():
        total_count             = ContactUs.count()
        result                  = ContactUs.list(limit=limit_int, offset=offset)
    
    logger.debug('manage_contact_us_listing: total_count=%s', total_count)
    
    for m in result:
        contact_us_list.append(m.to_dict())
    
       
    pager       = Pager(page_no_int, total_count, limit_int, show_only_next_and_previous=False)
    pages       = pager.get_pages()
    
    return render_template('admin/manage_contact_us/manage_contact_us_index.html', 
                           page_title                   = gettext('Contact Us History Listing'),
                           pagination_limit             = limit_int, 
                           page_url                     = url_for('manage_contact_us_bp.manage_contact_us_listing'),
                           contact_us_list              = contact_us_list,
                           end_point                    = 'manage_contact_us_bp.list_contact_us',
                           pager                        = pager,
                           pages                        = pages,
                           pagination_target_selector   = '#contact_us_listing_div',
                           )



        
    
        
@manage_contact_us_bp.route('/contact-us-listing/all/page-size/<limit>/page/<page_no>', methods=['GET'])
def list_contact_us(limit, page_no): 
    logger.debug('---list_contact_us---')
    
    logger.debug('page_no=%s', page_no)
    
    page_no_int         = int(page_no, 10)
    
    offset              = get_offset_by_page_no(page_no, limit=limit)
    total_count         = 0
    contact_us_list     = []
    limit_int           = int(limit, 10)
    
    try:
        db_client = create_db_client(caller_info="list_merchant")
        
        with db_client.context():
            total_count             = ContactUs.count()
            result                  = ContactUs.list(limit=limit_int, offset=offset)
        
        #logger.debug('list_merchant: result=%s', result)
        
        for m in result:
            contact_us_list.append(m.to_dict())
        
           
        pager       = Pager(page_no_int, total_count, limit_int, show_only_next_and_previous=False)
        pages       = pager.get_pages()
        
        
        return render_template('admin/manage_contact_us/contact_us_listing_content.html', 
                               contact_us_list              = contact_us_list,
                               end_point                    = 'manage_contact_us_bp.list_contact_us',
                               pager                        = pager,
                               pages                        = pages,
                               pagination_target_selector   = '#contact_us_listing_div',
                               )
    
    except:
        logger.error('Fail to list contact us due to %s', get_tracelog())
        
        return create_rest_message(status_code=StatusCode.BAD_REQUEST)

@manage_contact_us_bp.route('/contact-us-message/<contact_us_key>', methods=['GET'])
@login_required
def read_contact_us_message(contact_us_key): 
    logger.debug('---read_contact_us_message---')
    
    logger.debug('contact_us_key=%s', contact_us_key)
    
    if is_not_empty(contact_us_key):
        try:
            
            merchant_acct = None    
                
            db_client = create_db_client(caller_info="read_contact_us_message")
            
            with db_client.context():
                contact_us = ContactUs.fetch(contact_us_key)
            
            contact_us_dict = contact_us.to_dict()
            
            logger.debug('contact_us_dict=%s', contact_us_dict)
            
            return render_template('admin/manage_contact_us/contact_us_message.html', 
                                   page_title       = 'Contact Us Message',
                                   contact_us       = contact_us_dict,
                                   page_url         = url_for('manage_contact_us_bp.read_contact_us_message', contact_us_key=contact_us_key),
                                   ) 
                
        except:
            logger.error('Fail to read merchant account details due to %s', get_tracelog())
            
            return create_rest_message(status_code=StatusCode.BAD_REQUEST)
    else:
        return create_rest_message(status_code=StatusCode.BAD_REQUEST)       
