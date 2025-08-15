'''
Created on 23 Feb 2022

@author: jacklok
'''
from flask import Blueprint, render_template, request
from trexmodel.utils.model.model_util import create_db_client
from trexadmin.libs.http import StatusCode, create_rest_message
from trexadmin.libs.flask.decorator.security_decorators import login_required
import logging
from trexlib.utils.string_util import is_not_empty
from flask.helpers import url_for
from flask_babel import gettext
from trexadmin.libs.flask.utils.flask_helper import get_loggedin_merchant_user_account
from trexmodel.models.datastore.merchant_models import MerchantAcct
from trexmodel.models.datastore.pos_models import DinningOption, PosPaymentMethod
from trexadmin.forms.merchant.pos_forms import DinningOptionForm,\
    PosPaymentMethodForm

pos_payment_method_bp = Blueprint('pos_payment_method_bp', __name__,
                     template_folder='templates',
                     static_folder='static',
                     url_prefix='/merchant/pos/payment-method')

#logger = logging.getLogger('controller')
logger = logging.getLogger('debug')

@pos_payment_method_bp.context_processor
def pos_payment_method_bp_settings_bp_inject_settings():
    
    return dict(
                
                )


@pos_payment_method_bp.route('/', methods=['GET'])
@login_required
def pos_payment_method_listing(): 
    logged_in_merchant_user     = get_loggedin_merchant_user_account()
    db_client                   = create_db_client(caller_info="pos_payment_method_listing")
    payment_method_list    = []
    with db_client.context():
        merchant_acct   = MerchantAcct.get_or_read_from_cache(logged_in_merchant_user.get('merchant_acct_key'))
        result          = PosPaymentMethod.list_by_merchant_acct(merchant_acct)
        for r in result:
            payment_method_list.append(r.to_dict())
    
    return render_template('merchant/pos/payment_method/payment_method_listing.html',
                           page_title                   = gettext('Payment Method Setup'),
                           add_url                      = url_for('pos_payment_method_bp.add_pos_payment_method'),
                           reload_url                   = url_for('pos_payment_method_bp.pos_payment_method_listing_content'),
                           payment_method_list          = payment_method_list,
                           )

@pos_payment_method_bp.route('/listing-content', methods=['GET'])
@login_required
def pos_payment_method_listing_content(): 
    logged_in_merchant_user         = get_loggedin_merchant_user_account()
    db_client                       = create_db_client(caller_info="pos_payment_method_listing_content")
    payment_method_list             = []
    with db_client.context():
        merchant_acct   = MerchantAcct.get_or_read_from_cache(logged_in_merchant_user.get('merchant_acct_key'))
        result          = PosPaymentMethod.list_by_merchant_acct(merchant_acct)
        for r in result:
            payment_method_list.append(r.to_dict())
    
    return render_template('merchant/pos/payment_method/payment_method_listing_content.html',
                           payment_method_list = payment_method_list,
                           )

@pos_payment_method_bp.route('/add', methods=['GET'])
@login_required
def add_pos_payment_method(): 
    
    return render_template('merchant/pos/payment_method/payment_method.html',
                           page_title                     = gettext('Payment Method'),
                           submit_payment_method_url      = url_for('pos_payment_method_bp.add_payment_method_post'),
                           
                           ) 
    
@pos_payment_method_bp.route('/add', methods=['POST'])
@login_required
def add_payment_method_post():
    submit_payment_method_data       = request.form
    logged_in_merchant_user         = get_loggedin_merchant_user_account()
    
    logger.debug('submit_payment_method_data=%s', submit_payment_method_data)
    
    payment_method_form        = PosPaymentMethodForm(submit_payment_method_data)
    if payment_method_form.validate():
        payment_method_key          = payment_method_form.payment_method_key.data
        label                       = payment_method_form.label.data
        is_default                  = payment_method_form.is_default.data  
        is_rounding_required        = payment_method_form.is_rounding_required.data
        
        db_client       = create_db_client(caller_info="add_payment_method_post")
        with db_client.context():
            merchant_acct           = MerchantAcct.get_or_read_from_cache(logged_in_merchant_user.get('merchant_acct_key'))
            if is_not_empty(payment_method_key):
                payment_method = PosPaymentMethod.fetch(payment_method_key)
                if payment_method:
                    PosPaymentMethod.update(payment_method, label, is_default=is_default, is_rounding_required=is_rounding_required)
            else:
                payment_method = PosPaymentMethod.create(label, merchant_acct, is_default=is_default, is_rounding_required=is_rounding_required)
            
        if payment_method:
            return create_rest_message(gettext('Payment method have been created'), 
                                                payment_method_key  = payment_method.key_in_str,
                                                status_code         = StatusCode.OK,
                                                )
            
    else:
        error_message = payment_method_form.create_rest_return_error_message()
        
        logger.error('error_message=%s', error_message)
        
        return create_rest_message(error_message, status_code=StatusCode.BAD_REQUEST)
    
@pos_payment_method_bp.route('/<payment_method_key>', methods=['GET'])
@login_required
def read_payment_method(payment_method_key):    
    
    
    db_client       = create_db_client(caller_info="read_payment_method")
    
    with db_client.context():
        payment_method = PosPaymentMethod.fetch(payment_method_key)
        if payment_method:
            payment_method = payment_method.to_dict()
        
    return render_template('merchant/pos/payment_method/payment_method.html',
                       page_title                       = gettext('Payment Method'),
                       submit_payment_method_url        = url_for('pos_payment_method_bp.add_payment_method_post'),
                       payment_method                   = payment_method,
                       )
    
@pos_payment_method_bp.route('/<payment_method_key>/archive', methods=['POST'])
@login_required
def archive_payment_method_post(payment_method_key):
    db_client       = create_db_client(caller_info="archive_payment_method_post")
    with db_client.context():
        payment_method = PosPaymentMethod.fetch(payment_method_key)
        if payment_method:
            PosPaymentMethod.archive(payment_method)
    
    return create_rest_message(gettext('Payment method have been archived'), 
                                                status_code             = StatusCode.ACCEPTED,
                                                )  