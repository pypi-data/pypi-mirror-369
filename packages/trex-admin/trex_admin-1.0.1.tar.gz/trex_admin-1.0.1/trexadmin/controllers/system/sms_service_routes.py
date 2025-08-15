'''
Created on 11 Jul 2024

@author: jacklok
'''
import os, json
from flask import Blueprint, render_template, request, current_app, jsonify
from trexlib.utils.log_util import get_tracelog
from trexlib.utils.string_util import is_not_empty
import logging
from flask.helpers import url_for
from trexmodel.utils.model.model_util import create_db_client
from trexmodel.models.datastore.merchant_models import MerchantSentEmail


sms_service_bp = Blueprint('mailjet_service_bp', __name__,
                                     template_folder    = 'templates',
                                     static_folder      = 'static',
                                     url_prefix         = '/system/mailjet-service'
                                     )


logger = logging.getLogger('application:mail_service_routes')

