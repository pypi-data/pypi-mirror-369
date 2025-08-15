'''
Created on 29 Nov 2024

@author: jacklok
'''

from flask.blueprints import Blueprint
import logging
from trexmodel.models.datastore.analytic_models import UpstreamData
from trexmodel.utils.model.model_util import create_db_client
from flask.json import jsonify
from trexlib.utils.google.bigquery_util import create_bigquery_client,\
    create_table_from_template
from trexconf.conf import BIGQUERY_SERVICE_CREDENTIAL_PATH, MERCHANT_DATASET
from datetime import datetime
from trexanalytics.bigquery_table_template_config import USER_VOUCHER_REMOVED_TEMPLATE,\
    TABLE_SCHEME_TEMPLATE, USER_VOUCHER_REDEEMED_TEMPLATE
from trexmodel.models.datastore.merchant_models import MerchantAcct
from trexadmin.libs.http import create_rest_message, StatusCode

manage_merchant_task_bp = Blueprint('manage_merchant_task_bp', __name__,
                     template_folder    = 'templates',
                     static_folder      = 'static',
                     url_prefix         = '/merchant/task'
                     )

logger = logging.getLogger('controller')

@manage_merchant_task_bp.context_processor
def inject_settings():
    return dict()

@manage_merchant_task_bp.route('/merchant-key/<merchant_key>/create-required-analytics-table', methods=['GET'])
def create_merchant_required_analytics_table(merchant_key):
    now = datetime.utcnow()
    year_month_day = datetime.strftime(now, '%Y%m%d')
    
    db_client = create_db_client(caller_info="create_merchant_required_analytics_table")
    
    with db_client.context():
        merchant_acct = MerchantAcct.fetch(merchant_key)
    
    if merchant_acct:
        account_code = merchant_acct.account_code
        bq_client    = create_bigquery_client(credential_filepath=BIGQUERY_SERVICE_CREDENTIAL_PATH)
        
        account_code    = account_code.replace('-','')
        
        table_name = USER_VOUCHER_REMOVED_TEMPLATE
        final_table_name        = '{}_{}_{}'.format(table_name, account_code, year_month_day)
        
        created_table   = create_table_from_template(
                            MERCHANT_DATASET, 
                            final_table_name, 
                            TABLE_SCHEME_TEMPLATE.get(USER_VOUCHER_REMOVED_TEMPLATE), 
                            bigquery_client=bq_client)
        logger.info('create_merchant_required_analytics_table: created table(%s)=%s', final_table_name, created_table)
        
        table_name = USER_VOUCHER_REDEEMED_TEMPLATE
        final_table_name        = '{}_{}_{}'.format(table_name, account_code, year_month_day)
        
        created_table   = create_table_from_template(
                            MERCHANT_DATASET, 
                            final_table_name, 
                            TABLE_SCHEME_TEMPLATE.get(USER_VOUCHER_REDEEMED_TEMPLATE), 
                            bigquery_client=bq_client)
        logger.info('create_merchant_required_analytics_table: created table(%s)=%s', final_table_name, created_table)
        return create_rest_message('Updated since %s' % now, status_code=StatusCode.OK)
    else:
        return create_rest_message('Invalod merchant key', status_code=StatusCode.BAD_REQUEST)
