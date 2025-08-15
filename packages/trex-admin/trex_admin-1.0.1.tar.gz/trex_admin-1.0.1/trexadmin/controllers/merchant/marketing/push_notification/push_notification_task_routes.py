'''
Created on 16 Jan 2024

@author: jacklok
'''

from flask import Blueprint
import logging
from trexlib.utils.log_util import get_tracelog
from flask_restful import Api
from trexmodel.utils.model.model_util import create_db_client
from flask.globals import request
from flask.json import jsonify
from trexmodel.models.datastore.marketing_models import PushNotificationSetup
from trexadmin.libs.app.utils.push_notification_utils import create_topic_message
from trexadmin.libs.http import create_rest_message, StatusCode
from datetime import datetime
from trexlib.utils.string_util import is_not_empty, boolify
from _datetime import timedelta


push_notification_task_bp = Blueprint('push_notification_task_bp', __name__,
                     template_folder='templates',
                     static_folder='static',
                     url_prefix='/push-notification/task')

#logger = logging.getLogger('controller')
logger = logging.getLogger('target_debug')

@push_notification_task_bp.route('/setup/<push_notification_setup_key>', methods=['get'])
def send_push_notification(push_notification_setup_key, force=False):
    db_client = create_db_client(caller_info="send_push_notification")
    force_to_send_again = request.args.get('force', force)
    
    logger.debug('force_to_send_again=%s', force_to_send_again)
    
    if is_not_empty(force_to_send_again):
        force_to_send_again = boolify(force_to_send_again)
    else:
        force_to_send_again = False
    
    with db_client.context():
        push_notification_setup = PushNotificationSetup.fetch(push_notification_setup_key)
        
    if push_notification_setup:
        __send_push_notification(push_notification_setup, force_to_send_again=force_to_send_again)
        
        return create_rest_message(status_code=StatusCode.OK, 
                           sent_datetime = push_notification_setup.sent_datetime,
                           )
    else:
        return create_rest_message("Invalid push notification", status_code=StatusCode.BAD_REQUEST) 
    
def __send_push_notification(push_notification_setup, force_to_send_again=False):
    db_client = create_db_client(caller_info="__send_push_notification")
    with db_client.context():    
        merchant_acct   = push_notification_setup.merchant_acct_entity
        topic           = merchant_acct.account_code
        if (force_to_send_again==True or  push_notification_setup.send==False):
            image           = push_notification_setup.image_url
            text            = push_notification_setup.text_data
            action_link     = push_notification_setup.action_link
            analytics_label = None
            
            
            create_topic_message(
                push_notification_setup.title,
                push_notification_setup.desc,
                topic,
                analytics_label = analytics_label,
                image           = image,
                text            = text,
                action_link     = action_link,
                )
            
            push_notification_setup.update_as_send()
    

@push_notification_task_bp.route('/scheduled/datetime/<scheduled_datetime_str>', methods=['GET'])
def check_scheduled_datetime_push_notification(scheduled_datetime_str):
    return _check_scheduled_push_notification(scheduled_datetime_str)

@push_notification_task_bp.route('/scheduled/now', methods=['GET'])
def check_scheduled_now_push_notification():
    return _check_scheduled_push_notification(None)

def _check_scheduled_push_notification(scheduled_datetime_str):
    force_to_send_again = request.args.get('force')
    
    if is_not_empty(force_to_send_again):
        force_to_send_again = boolify(force_to_send_again)
    else:
        force_to_send_again = False
        
    db_client = create_db_client(caller_info="_check_scheduled_push_notification")
    result_list = []
    
    logger.debug('force_to_send_again=%s', force_to_send_again)
    
    try:
        last_scheduled_datetime = None
        if is_not_empty(scheduled_datetime_str):
            scheduled_datetime = datetime.strptime(scheduled_datetime_str, '%Y-%m-%d %H:%M:%S')
            
        else:
            scheduled_datetime = datetime.utcnow()
        
        last_scheduled_datetime =scheduled_datetime - timedelta(hours=4)
         
        logger.debug('last_scheduled_datetime=%s', last_scheduled_datetime)
        logger.debug('scheduled_datetime=%s', scheduled_datetime) 
         
        with db_client.context():
            scheduled_push_notification_list = PushNotificationSetup.list(
                                                                        start_datetime=last_scheduled_datetime,  
                                                                        end_datetime=scheduled_datetime,
                                                                        send=force_to_send_again,
                                                                        )
        
        logger.debug('scheduled_push_notification_list count=%s', len(scheduled_push_notification_list))
        
        if scheduled_push_notification_list:
            for r in scheduled_push_notification_list:
                __send_push_notification(r, force_to_send_again=force_to_send_again)
                result_list.append(r.to_dict())
    except:
        logger.error('Fail to check scheduled push notification due to %s', get_tracelog())
        
    return jsonify(result_list)    