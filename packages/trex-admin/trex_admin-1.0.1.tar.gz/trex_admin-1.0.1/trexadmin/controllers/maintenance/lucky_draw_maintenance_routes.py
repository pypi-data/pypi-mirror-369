'''
Created on 26 Nov 2024

@author: jacklok
'''

from flask import Blueprint, request
from trexmodel.utils.model.model_util import create_db_client
import logging
from flask_restful import Api
from trexlib.libs.controllers.task_base_routes import TriggerTaskBaseResource,\
    InitTaskBaseResource, TaskBaseResource
from trexmodel.models.datastore.merchant_models import MerchantAcct
from trexmodel.models.datastore.lucky_draw_models import LuckyDrawTicket

lucky_draw_maintenance_setup_bp = Blueprint('lucky_draw_maintenance_setup_bp', __name__,
                     template_folder='templates',
                     static_folder='static',
                     url_prefix='/maint/lucky-draw')


#logger = logging.getLogger('controller')
logger = logging.getLogger('maint')

lucky_draw_maintenance_setup_bp_api = Api(lucky_draw_maintenance_setup_bp)

class TriggerUpdateLuckyDrawTicket(TriggerTaskBaseResource):
    
    def get_task_url(self):
        return '/maint/lucky-draw/init-update-ticket'
    
    def get_task_queue(self):
        return 'upstream-maint'
        
    def get_data_payload(self):
        merchant_key    = request.args.get('merchant_key')
        program_key     = request.args.get('program_key')
        return {
                'merchant_key'  : merchant_key,
                'program_key'   : program_key,
            }    
    
class InitUpdateLuckyDrawTicket(InitTaskBaseResource):
    def get_task_count(self, **kwargs):
        merchant_key    = kwargs.get('merchant_key')
        db_client = create_db_client(caller_info="InitImportVoucherUpstream")
    
        with db_client.context():
            merchant_acct = MerchantAcct.fetch(merchant_key)
            count = LuckyDrawTicket.count_by_merchant_acct(merchant_acct)
        
        return count
    
    def get_task_batch_size(self):
        return 100
    
    def get_task_url(self):
        return '/maint/lucky-draw/update-ticket'
    
    def get_task_queue(self):
        return 'test'
    
    
    def get_data_payload(self):
        merchant_key    = request.get_json().get('merchant_key')
        program_key     = request.get_json().get('program_key')
        return {
                'merchant_key'  : merchant_key,
                'program_key'   : program_key,
            }
    
class ExecuteUpdateLuckyDrawTicket(TaskBaseResource):
    def execute_task(self, offset, limit, **kwargs):
        merchant_key    = kwargs.get('merchant_key')
        program_key    = kwargs.get('program_key')
        start_cursor    = kwargs.get('start_cursor')
        task_index      = int(kwargs.get('task_index'))
        
        logger.debug('execute_task debug: merchant_key=%s task_index=%d, offset=%d, limit=%d', merchant_key, task_index, offset, limit)
        
        db_client = create_db_client(caller_info="ExecuteUpdateLuckyDrawTicket")
    
        with db_client.context():
            merchant_acct               = MerchantAcct.fetch(merchant_key)
            (result, next_cursor)       = LuckyDrawTicket.list_by_merchant_acct(merchant_acct, offset=offset, limit=limit, start_cursor=start_cursor)
            
            if result:
                
                for ticket in result:
                    ticket.program_key = program_key
                    ticket.put()
        
        return next_cursor
        
    def get_task_queue(self):
        return 'test'   
    
    def get_task_url(self):
        return '/maint/lucky-draw/update-ticket' 

    def get_data_payload(self):
        merchant_key    = request.get_json().get('merchant_key')
        program_key     = request.get_json().get('program_key')
        return {
                'merchant_key'  : merchant_key,
                'program_key'   : program_key,
            }   


lucky_draw_maintenance_setup_bp_api.add_resource(TriggerUpdateLuckyDrawTicket,   '/trigger-update-ticket')
lucky_draw_maintenance_setup_bp_api.add_resource(InitUpdateLuckyDrawTicket,   '/init-update-ticket')
lucky_draw_maintenance_setup_bp_api.add_resource(ExecuteUpdateLuckyDrawTicket,   '/update-ticket')
