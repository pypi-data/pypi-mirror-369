'''
Created on 8 Jan 2021

@author: jacklok
'''
from flask import Blueprint, render_template, request, Response
from trexadmin.libs.flask.utils.flask_helper import output_html
from flask_restful import Resource, Api
import logging
from flask_httpauth import HTTPBasicAuth
from trexconf import conf
from trexmodel.utils.model.model_util import create_db_client
from trexmodel.models.datastore.merchant_models import MerchantUser
import hashlib

api_bp = Blueprint('api_bp', __name__,
                     template_folder='templates',
                     static_folder='static',
                     url_prefix='/api')


auth = HTTPBasicAuth()

logger = logging.getLogger('api')

api = Api(api_bp)

@auth.verify_password
def verify_user_auth(username, password):
    if not (username and password):
        return False
    
    db_client   = create_db_client(caller_info="verify_user_auth")
    valid_auth  = False
    
    with db_client.context():
        merchant_user = MerchantUser.get_by_username(username)
        
        if merchant_user:
            
            md5_hashed_password = hashlib.md5(password.encode('utf-8')).hexdigest()
            
            logger.debug('verify_user_auth: username=%s', username)
            logger.debug('verify_user_auth: password=%s', password)
            logger.debug('verify_user_auth: md5_hashed_password=%s', md5_hashed_password)
            
            if merchant_user.is_valid_password(md5_hashed_password):
                valid_auth = True
            else:
                logger.warn('Invalid merchant password')
        else:
            logger.warn('Invalid merchant username=%s', username)
            
    return valid_auth


class ApiVersionResource(Resource):
    @auth.login_required
    def get(self):
        return conf.APPLICATION_VERSION_NO
    


api.add_resource(ApiVersionResource, '/version')