'''
Created on 23 May 2023

@author: jacklok
'''

from flask import Blueprint, render_template
import logging
from flask_login.utils import login_required
from trexmodel.utils.model.model_util import create_db_client
from trexlib.utils.log_util import get_tracelog
from flask_babel import gettext
from flask.helpers import url_for

app_promotion_setup_bp = Blueprint('app_promotion_setup_bp', __name__,
                     template_folder='templates',
                     static_folder='static',
                     url_prefix='/app/promotion/setup')


logger = logging.getLogger('controller')

'''
Blueprint settings here
'''
@app_promotion_setup_bp.context_processor
def app_promotion_bp_inject_settings():
    
    return dict(
               
               
                )

@app_promotion_setup_bp.route('/', methods=['GET'])
@login_required
def app_promotion_setup_listing(): 
    return show_app_promotion_setup_listing('app/promotion/app_promotion_setup_listing.html')

@app_promotion_setup_bp.route('/', methods=['GET'])
@login_required
def app_promotion_setup_listing_content(): 
    return show_app_promotion_setup_listing('app/promotion/app_promotion_setup_listing_content.html')


def show_app_promotion_setup_listing(template_name, show_page_title=True):
    app_promotion_setup_list           = []
    
    db_client = create_db_client(caller_info="show_app_promotion_setup_listing")
    try:
        with db_client.context():
            pass
                
                        
            
    except:
        logger.error('Fail to list lucky draw due to %s', get_tracelog())
           
    
    logger.debug('promotion list count=%d', len(app_promotion_setup_list))
            
    return render_template(template_name,
                           page_title                                   = gettext('Promotion Setup') if show_page_title else None,
                           page_url                                     = url_for('app_promotion_setup_bp.app_promotion_setup_listing') if show_page_title else None,
                           add_app_promotion_setup_url                  = url_for('app_promotion_setup_bp.add_app_promotion_setup'),
                           reload_app_promotion_setup_listing_url       = url_for('app_promotion_setup_bp.list_app_promotion_setup_content'),
                           archived_app_promotion_setup_listing_url     = url_for('app_promotion_setup_bp.archive_app_promotion_setup_post'),
                           app_promotion_setup_list                     = app_promotion_setup_list,
                           show_tips                                    = show_page_title,
                           )


@app_promotion_setup_bp.route('/add', methods=['GET'])
@login_required
def add_app_promotion_setup__post():
    pass    

@app_promotion_setup_bp.route('/edit', methods=['POST'])
@login_required
def edit_app_promotion_setup__post():
    pass

@app_promotion_setup_bp.route('/archive-app-promotion', methods=['POST','GET'])
@login_required
def archive_app_promotion_setup__post(): 
    pass

    
