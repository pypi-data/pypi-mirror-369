'''
Created on 8 Sep 2021

@author: jacklok
'''
from flask import Blueprint, render_template
from trexadmin.libs.flask.decorator.security_decorators import login_required
import logging
from flask.helpers import url_for
from flask_babel import gettext

reward_program_overview_bp = Blueprint('reward_program_overview_bp', __name__,
                     template_folder='templates',
                     static_folder='static',
                     url_prefix='/merchant/reward-program/overview/')


logger = logging.getLogger('controller')

'''
Blueprint settings here
'''
@reward_program_overview_bp.context_processor
def reward_program_overview_bp_inject_settings():
    
    return dict(
                )
    
@reward_program_overview_bp.route('/', methods=['GET'])
@login_required
def reward_program_overview():
    return render_template('merchant/loyalty/reward_program/reward_program_overview.html', 
                           page_title                   = gettext('Reward Program Overview'),
                           page_url                     = url_for('reward_program_overview_bp.reward_program_overview'),
                           )
    