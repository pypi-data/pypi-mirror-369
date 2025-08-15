'''
Created on 28 Jan 2022

@author: jacklok
'''

from flask import Blueprint, render_template, request, url_for
from trexmodel.utils.model.model_util import create_db_client
from trexadmin.libs.http import StatusCode, create_rest_message
from trexadmin.libs.flask.decorator.security_decorators import login_required
import logging
from trexlib.utils.string_util import is_not_empty
from flask_babel import gettext
from trexadmin.libs.flask.utils.flask_helper import get_loggedin_merchant_user_account
from trexmodel.models.datastore.merchant_models import MerchantAcct
from trexmodel.models.datastore.pos_models import DinningOption
from trexadmin.forms.merchant.pos_forms import DinningOptionForm

dinning_option_bp = Blueprint('dinning_option_bp', __name__,
                     template_folder='templates',
                     static_folder='static',
                     url_prefix='/merchant/pos/dinning-option')

logger = logging.getLogger('controller')
#logger = logging.getLogger('debug')

@dinning_option_bp.context_processor
def dinning_option_bp_source_bp_settings_bp_inject_settings():
    
    return dict(
                
                )


@dinning_option_bp.route('/', methods=['GET'])
@login_required
def dinning_option_listing(): 
    logged_in_merchant_user     = get_loggedin_merchant_user_account()
    db_client                   = create_db_client(caller_info="dinning_option_listing")
    dinning_option_list    = []
    with db_client.context():
        merchant_acct   = MerchantAcct.get_or_read_from_cache(logged_in_merchant_user.get('merchant_acct_key'))
        result          = DinningOption.list_by_merchant_acct(merchant_acct)
        for r in result:
            dinning_option_list.append(r.to_dict())
    
    return render_template('merchant/pos/dinning_option/dinning_option_listing.html',
                           page_title                   = gettext('Dinning Option Setup'),
                           add_url                      = url_for('dinning_option_bp.add_dinning_option'),
                           reload_url                   = url_for('dinning_option_bp.dinning_option_listing_content'),
                           dinning_option_list          = dinning_option_list,
                           )

@dinning_option_bp.route('/listing-content', methods=['GET'])
@login_required
def dinning_option_listing_content(): 
    logged_in_merchant_user         = get_loggedin_merchant_user_account()
    db_client                       = create_db_client(caller_info="dinning_option_listing_content")
    dinning_option_list             = []
    with db_client.context():
        merchant_acct   = MerchantAcct.get_or_read_from_cache(logged_in_merchant_user.get('merchant_acct_key'))
        result          = DinningOption.list_by_merchant_acct(merchant_acct)
        for r in result:
            dinning_option_list.append(r.to_dict())
    
    return render_template('merchant/pos/dinning_option/dinning_option_listing_content.html',
                           dinning_option_list = dinning_option_list,
                           )
    
@dinning_option_bp.route('/add', methods=['GET'])
@login_required
def add_dinning_option(): 
    
    return render_template('merchant/pos/dinning_option/dinning_option.html',
                           page_title                     = gettext('Dinning Option'),
                           submit_dinning_option_url      = url_for('dinning_option_bp.add_dinning_option_post'),
                           
                           ) 
    
@dinning_option_bp.route('/add', methods=['POST'])
@login_required
def add_dinning_option_post():
    submit_dinning_option_data          = request.form
    logged_in_merchant_user             = get_loggedin_merchant_user_account()
    
    logger.debug('submit_dinning_option_data=%s', submit_dinning_option_data)
    
    dinning_option_form        = DinningOptionForm(submit_dinning_option_data)
    if dinning_option_form.validate():
        dinning_option_key          = dinning_option_form.dinning_option_key.data
        name                        = dinning_option_form.name.data
        prefix                      = dinning_option_form.prefix.data
        is_default                  = dinning_option_form.is_default.data    
        is_dinning_input            = dinning_option_form.is_dinning_input.data
        is_delivery_input           = dinning_option_form.is_delivery_input.data    
        is_takeaway_input           = dinning_option_form.is_takeaway_input.data
        is_self_order_input         = dinning_option_form.is_self_order_input.data
        dinning_table_is_required   = dinning_option_form.dinning_table_is_required.data
        is_self_payment_mandatory   = dinning_option_form.is_self_payment_mandatory.data
        assign_queue                = dinning_option_form.assign_queue.data
        
        db_client       = create_db_client(caller_info="add_dinning_option_post")
        
        with db_client.context():
            merchant_acct           = MerchantAcct.get_or_read_from_cache(logged_in_merchant_user.get('merchant_acct_key'))
            if is_not_empty(dinning_option_key):
                dinning_option = DinningOption.fetch(dinning_option_key)
                if dinning_option:
                    DinningOption.update(dinning_option, name, prefix, is_dinning_input=is_dinning_input, 
                                         is_delivery_input=is_delivery_input, is_takeaway_input=is_takeaway_input, 
                                         is_self_order_input=is_self_order_input, is_default=is_default, 
                                         dinning_table_is_required=dinning_table_is_required, assign_queue=assign_queue,
                                         is_self_payment_mandatory=is_self_payment_mandatory)
            else:
                dinning_option = DinningOption.create(name, prefix, merchant_acct, is_dinning_input=is_dinning_input, 
                                                      is_delivery_input=is_delivery_input, is_takeaway_input=is_takeaway_input, 
                                                      is_self_order_input=is_self_order_input, is_default=is_default, 
                                                      dinning_table_is_required=dinning_table_is_required, 
                                                      assign_queue=assign_queue,
                                                      is_self_payment_mandatory=is_self_payment_mandatory)
            
        if dinning_option:
            return create_rest_message(gettext('Dinning option have been created'), 
                                                dinning_option_key  = dinning_option.key_in_str,
                                                status_code         = StatusCode.OK,
                                                )
            
    else:
        error_message = dinning_option_form.create_rest_return_error_message()
        
        logger.error('error_message=%s', error_message)
        
        return create_rest_message(error_message, status_code=StatusCode.BAD_REQUEST)
    
@dinning_option_bp.route('/<dinning_option_key>', methods=['GET'])
@login_required
def read_dinning_option(dinning_option_key):    
    
    
    db_client       = create_db_client(caller_info="read_dinning_option")
    
    with db_client.context():
        dinning_option = DinningOption.fetch(dinning_option_key)
        if dinning_option:
            dinning_option = dinning_option.to_dict()
        
    return render_template('merchant/pos/dinning_option/dinning_option.html',
                       page_title                       = gettext('Dinning Option'),
                       submit_dinning_option_url        = url_for('dinning_option_bp.add_dinning_option_post'),
                       dinning_option                   = dinning_option,
                       )
    
@dinning_option_bp.route('/<dinning_option_key>/archive', methods=['POST'])
@login_required
def archive_dinning_option_post(dinning_option_key):
    db_client       = create_db_client(caller_info="archive_dinning_option_post")
    with db_client.context():
        dinning_option = DinningOption.fetch(dinning_option_key)
        if dinning_option:
            DinningOption.archive(dinning_option)
    
    return create_rest_message(gettext('Dinning option have been archived'), 
                                                status_code             = StatusCode.ACCEPTED,
                                                )        