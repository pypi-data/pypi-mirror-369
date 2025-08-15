'''
Created on 23 Apr 2024

@author: jacklok
'''
from flask import Blueprint
from trexmodel.utils.model.model_util import create_db_client
import logging
from flask_restful import Api
from trexlib.libs.controllers.task_base_routes import TriggerTaskBaseResource,\
    InitTaskBaseResource, TaskBaseResource
from trexmodel.models.datastore.user_models import User
from trexlib.utils.string_util import random_string

user_maintenance_bp = Blueprint('user_maintenance_bp', __name__,
                     template_folder='templates',
                     static_folder='static',
                     url_prefix='/maint/user')


#logger = logging.getLogger('controller')
logger = logging.getLogger('controller')

user_maintenance_bp_api = Api(user_maintenance_bp)


class TriggerUpdateUser(TriggerTaskBaseResource):
    
    def get_task_url(self):
        return '/maint/user/init-update-user'
    
    def get_task_queue(self):
        return 'test'
        
    def get_data_payload(self):
        return {
        
            }    
    
class InitUpdateUser(InitTaskBaseResource):
    def get_task_count(self, **kwargs):
        count = 0
        db_client = create_db_client(caller_info="InitUpdateUser")
    
        with db_client.context():
            count = User.count_all()
        
        return count
    
    def get_task_batch_size(self):
        return 50
    
    def get_task_url(self):
        return '/maint/user/update-user'
    
    def get_task_queue(self):
        return 'test'
    
    
    def get_data_payload(self):
        return {
        
            }
    
class ExecuteUpdateUser(TaskBaseResource):
    def execute_task(self, offset, limit, **kwargs):
        start_cursor    = kwargs.get('start_cursor')
        task_index      = int(kwargs.get('task_index'))
        
        logger.debug('execute_task debug: task_index=%d, offset=%d, limit=%d', task_index, offset, limit)
        
        db_client = create_db_client(caller_info="ExecuteResetCustomerKPI")
    
        with db_client.context():
            (result, next_cursor)       = User.list_all(offset=offset, start_cursor=start_cursor, return_with_cursor=True, limit=limit)
            
            if result:
                
                for user in result:
                    
                    user.referral_code = random_string(8, is_human_mistake_safe=True)
                    user.put()
                    
            
        
        return next_cursor
        
    def get_task_queue(self):
        return 'test'   
    
    def get_task_url(self):
        return '/maint/user/update-user' 

    def get_data_payload(self):
        return {
        
            }  

user_maintenance_bp_api.add_resource(TriggerUpdateUser,   '/trigger-update-user')
user_maintenance_bp_api.add_resource(InitUpdateUser,   '/init-update-user')
user_maintenance_bp_api.add_resource(ExecuteUpdateUser,   '/update-user')
