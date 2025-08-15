'''
Created on 11 Oct 2024

@author: jacklok
'''
from flask.blueprints import Blueprint
import logging
from trexadmin.libs.flask.decorator.security_decorators import login_required
from flask.templating import render_template
from flask_babel import gettext
from trexadmin.libs.flask.utils.flask_helper import get_merchant_configured_currency_details


merchant_tour_bp = Blueprint('merchant_tour_bp', __name__,
                     template_folder='templates',
                     static_folder='static',
                     url_prefix='/merchant/tour')

logger = logging.getLogger('controller')

'''
Blueprint settings here
'''
@merchant_tour_bp.context_processor
def merchant_tour_bp_inject_settings():
    return {
            
            }
    
@merchant_tour_bp.route('/')
@login_required
def tour_page(): 
    
    return render_template("merchant/tour/setup_steps_page.html",
                           page_title    = gettext('Setup Guide'),
                           currency_details            = get_merchant_configured_currency_details()
                               
                               )
    