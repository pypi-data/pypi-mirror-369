'''
Created on 13 Feb 2023

@author: jacklok
'''

from flask import Blueprint, render_template, session, abort, redirect, url_for, current_app
import logging, json, uuid
from trexlib.libs.controllers.task_base_routes import TriggerTaskBaseResource, InitTaskBaseResource, TaskBaseResource
from trexlib.utils.log_util import get_tracelog
from flask_restful import Api


test_task_bp = Blueprint('test_task_bp', __name__,
                     template_folder='templates',
                     static_folder='static',
                     url_prefix='/test/task')

test_task_bp_api = Api(test_task_bp)

logger = logging.getLogger('debug')

class TriggerPing(TriggerTaskBaseResource):
    
    def get_base_url(self):
        return 'https://636c-210-195-253-20.ngrok.io'
    
    def get_task_url(self):
        return '/test/task/init-ping'
    
    def get_task_queue(self):
        return 'test'
        
    def get_data_payload(self):
        return {
                'data1': 'test1',
                'data2': 'test2',
            }    
    
class InitPing(InitTaskBaseResource):
    def get_task_count(self, **kwargs):
        return 3
    
    def get_task_batch_size(self):
        return 1
    
    def get_task_url(self):
        return '/test/task/execute-ping'
    
    def get_task_queue(self):
        return 'test'
    
class ExecutePing(TaskBaseResource):
    def execute_task(self, offset, limit, **kwargs):
        logger.debug('Ping offset=%d, limit=%d', offset, limit)       
        
    def get_task_queue(self):
        return 'test'   
    
    def get_task_url(self):
        return '/test/task/execute-ping'  


test_task_bp_api.add_resource(TriggerPing,   '/trigger-ping')
test_task_bp_api.add_resource(InitPing,   '/init-ping')
test_task_bp_api.add_resource(ExecutePing,   '/execute-ping')
