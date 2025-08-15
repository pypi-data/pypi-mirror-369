'''
Created on 19 Feb 2021

@author: jacklok
'''

from flask import Blueprint, render_template
from trexadmin.libs.flask.decorator.security_decorators import login_required
import logging
from flask.helpers import url_for
from flask_babel import gettext

reward_program_set_fraud_prevention_bp = Blueprint('reward_program_set_fraud_prevention_bp', __name__,
                     template_folder='templates',
                     static_folder='static',
                     url_prefix='/merchant/reward-program/fraud-prevention/')


logger = logging.getLogger('controller')

'''
Blueprint settings here
'''
@reward_program_set_fraud_prevention_bp.context_processor
def reward_program_set_fraud_prevention_bp_inject_settings():
    
    return dict(
                
                
                )

@reward_program_set_fraud_prevention_bp.route('/', methods=['GET'])
@login_required
def set_fraud_prevention(): 
    logger.debug('---set_fraud_prevention---')
    
    
    return render_template('merchant/loyalty/reward_program/fraud_prevention/set_fraud_prevention.html', 
                           page_title           = gettext('Setup Fraud Prevention'),
                           page_url             = url_for('reward_program_set_fraud_prevention_bp.set_fraud_prevention'),
                           )
