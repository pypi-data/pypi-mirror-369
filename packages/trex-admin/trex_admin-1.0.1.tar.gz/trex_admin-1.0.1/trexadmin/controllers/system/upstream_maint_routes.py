'''
Created on 2 May 2024

@author: jacklok
'''
from flask.blueprints import Blueprint
import logging
from trexmodel.models.datastore.analytic_models import UpstreamData
from trexmodel.utils.model.model_util import create_db_client
from flask.json import jsonify

upstream_maint_bp = Blueprint('upstream_maint_bp', __name__,
                     template_folder    = 'templates',
                     static_folder      = 'static',
                     url_prefix         = '/system/upstream'
                     )

#from main import csrf


LANGUAGES = 'LANGUAGES'

#logger = logging.getLogger('system-controller')
logger = logging.getLogger('controller')

@upstream_maint_bp.context_processor
def inject_settings():
    return dict()

@upstream_maint_bp.route('/offset/<offset>/limit/<limit>', methods=['GET'])
def list_latest_not_send_upstream(offset, limit):
    db_client = create_db_client(caller_info="list_latest_upstream")
    
    with db_client.context():
        (upstream_data_list, next_cursor) = UpstreamData.list_not_send(offset=offset, limit=limit, return_with_cursor=True)
    
    return jsonify(upstream_data_list)
    
