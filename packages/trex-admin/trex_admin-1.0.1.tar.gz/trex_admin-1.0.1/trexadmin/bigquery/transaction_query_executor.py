'''
Created on 8 Jun 2021

@author: jacklok
'''
from datetime import datetime
from trexlib.utils.common import date_util
from trexconf import conf
from trexlib.utils.google.bigquery_util import execute_query, create_bigquery_client
import logging
from trexlib.utils.log_util import get_tracelog
from trexmodel.utils.model.model_util import create_db_client
from trexconf.conf import BIGQUERY_GCLOUD_PROJECT_ID, MERCHANT_DATASET
from trexlib.utils.common.date_util import date_str_to_bigquery_qualified_datetime_str,\
    date_to_bigquery_qualified_datetime_str

#logger = logging.getLogger('query')
logger = logging.getLogger('target_debug')


def query_reward_monthly_by_outlet(outlet, month, year):
    date_range_start    = datetime(year, month, 1)
    date_range_end      = datetime(year, month, date_util.last_day_of_month(date_range_start).day)
    
    bg_client       = create_bigquery_client(credential_filepath=conf.BIGQUERY_SERVICE_CREDENTIAL_PATH)
    
    db_client = create_db_client(caller_info="query_reward_monthly_by_outlet")
    with db_client.context():
        merchant_acct   = outlet.merchant_acct_entity
        account_code    = merchant_acct.account_code
        account_code    = account_code.replace('-','')
        
    if date_range_start and date_range_end:
        date_range_start    = date_to_bigquery_qualified_datetime_str(date_range_start)
        date_range_end      = date_to_bigquery_qualified_datetime_str(date_range_end)
        
        where_condition = "WHERE PartitionDateTime BETWEEN DATETIME('{date_range_start}') and DATETIME('{date_range_end}') and TransactOutlet='{transact_outlet}'".format(date_range_start=date_range_start,date_range_end=date_range_end, transact_outlet = outlet.key_in_str)
        
    dataset = '%s_%s' % (MERCHANT_DATASET,account_code)
        
    query = '''
        
        
            SELECT 
            FORMAT_DATETIME('%Y-%m-%d', RewardedDateTime) as RewardedDate, 
            TransactionId, RewardFormat, RewardFormatKey, FORMAT("%.2f", TransactAmount),
            SUM(RewardAmount) as TotalRewardAmount

            
                    FROM (
                        
                        SELECT
                            checking_transaction.RewardedDateTime as RewardedDateTime, 
                            checking_transaction.TransactionId as TransactionId, 
                            checking_transaction.UpdatedDateTime, 
                            checking_transaction.RewardFormat as RewardFormat,
                            checking_transaction.RewardFormatKey as RewardFormatKey,
                            checking_transaction.RewardAmount as RewardAmount,
                            checking_transaction.TransactAmount as TransactAmount,
                            checking_transaction.Reverted as Reverted
                            
                          FROM
                            (
                            SELECT
                               TransactionId, MAX(UpdatedDateTime) AS latestUpdatedDateTime
                             FROM
                               `{project_id}.{dataset_name}.customer_reward`
                                
                                {where_condition}
                        
                             GROUP BY
                               TransactionId
                               ) 
                               AS latest_transaction
                          INNER JOIN
                          (
                            SELECT 
                            RewardedDateTime, TransactionId, UpdatedDateTime, RewardFormat, RewardFormatKey, RewardAmount, TransactAmount, Reverted
                            FROM
                            `{project_id}.{dataset_name}.customer_reward`
                              
                              {where_condition}
                        
                          ) as checking_transaction
                        
                        ON
                        
                        checking_transaction.TransactionId = latest_transaction.TransactionId
                        AND
                        checking_transaction.UpdatedDateTime=latest_transaction.latestUpdatedDateTime
                        
                )
                WHERE Reverted=False
                GROUP BY RewardedDateTime, TransactionId, RewardFormat, RewardFormatKey, TransactAmount
        
        order by RewardedDate        
        '''.format(project_id=BIGQUERY_GCLOUD_PROJECT_ID, dataset_name=dataset, where_condition=where_condition, account_code=account_code) 
        
    logger.debug('query=%s', query);
    
    try:
        
        job_result_rows = execute_query(bg_client, query)
    except:
        job_result_rows = []
        logger.error('Failed to execute query due to %s', get_tracelog())
    
    
    row_list = []
    for row in job_result_rows:
        #logger.debug(row)
        column_dict = {}
        column_dict['RewardedDate']         = row.RewardedDate
        column_dict['TransactionId']        = row.TransactionId
        #column_dict['TotalPoints']          = row.TotalPoints
        #column_dict['TotalStamps']          = row.TotalStamps
        #column_dict['TransactAmount']       = row.TransactAmount
        column_dict['RewardFormat']         = row.RewardFormat
        column_dict['RewardFormatKey']      = row.RewardFormatKey
        column_dict['TotalRewardAmount']    = float(row.TotalRewardAmount)
        column_dict['TransactAmount']       = float(row.TransactAmount)
        
        
        row_list.append(column_dict)
    
    return row_list

def query_transaction_monthly_by_outlet(outlet, month, year):
    date_range_start    = datetime(year, month, 1)
    date_range_end      = datetime(year, month, date_util.last_day_of_month(date_range_start).day)
    
    bg_client       = create_bigquery_client(credential_filepath=conf.BIGQUERY_SERVICE_CREDENTIAL_PATH)
    
    db_client = create_db_client(caller_info="query_reward_monthly_by_outlet")
    with db_client.context():
        merchant_acct   = outlet.merchant_acct_entity
        account_code    = merchant_acct.account_code
        account_code    = account_code.replace('-','')
        
    if date_range_start and date_range_end:
        date_range_start    = date_to_bigquery_qualified_datetime_str(date_range_start)
        date_range_end      = date_to_bigquery_qualified_datetime_str(date_range_end)
        
        where_condition = "WHERE PartitionDateTime BETWEEN DATETIME('{date_range_start}') and DATETIME('{date_range_end}') and TransactOutlet='{transact_outlet}'".format(date_range_start=date_range_start,date_range_end=date_range_end, transact_outlet = outlet.key_in_str)
        
    dataset = '%s_%s' % (MERCHANT_DATASET,account_code)
        
    query = '''
        SELECT FORMAT_DATETIME('%Y-%m-%d', RewardedDateTime) as RewardedDate,  
                FORMAT("%.2f", sum(TotalTransactAmount)) as SumTransactAmount, count(transactionId) as TransactionCount
        FROM (
        
            SELECT transactionId, RewardedDateTime, SUM(TransactAmount) as TotalTransactAmount
                    FROM (
                        
                        SELECT
                            checking_transaction.RewardedDateTime as RewardedDateTime, 
                            checking_transaction.TransactionId as TransactionId, 
                            checking_transaction.UpdatedDateTime, 
                            checking_transaction.TransactAmount as TransactAmount,
                            checking_transaction.Reverted as Reverted
                            
                          FROM
                            (
                            SELECT
                               TransactionId, MAX(UpdatedDateTime) AS latestUpdatedDateTime
                             FROM
                               `{project_id}.{dataset_name}.customer_reward`
                                
                                {where_condition}
                        
                             GROUP BY
                               TransactionId
                               ) 
                               AS latest_transaction
                          INNER JOIN
                          (
                            SELECT 
                            RewardedDateTime, TransactionId, UpdatedDateTime, TransactAmount, Reverted
                            FROM
                            `{project_id}.{dataset_name}.customer_reward`
                              
                              {where_condition}
                        
                          ) as checking_transaction
                        
                        ON
                        
                        checking_transaction.TransactionId = latest_transaction.TransactionId
                        AND
                        checking_transaction.UpdatedDateTime=latest_transaction.latestUpdatedDateTime
                        
                )
                WHERE Reverted=False
                GROUP BY transactionId, RewardedDateTime
        )
        GROUP BY RewardedDate    
        order by RewardedDate        
        '''.format(project_id=BIGQUERY_GCLOUD_PROJECT_ID, dataset_name=dataset, where_condition=where_condition, account_code=account_code) 
        
    logger.debug('query=%s', query);
    
    try:
        
        job_result_rows = execute_query(bg_client, query)
    except:
        job_result_rows = []
        logger.error('Failed to execute query due to %s', get_tracelog())
    
    
    row_list = []
    for row in job_result_rows:
        #logger.debug(row)
        column_dict = {}
        column_dict['rewardedDate']         = row.RewardedDate
        column_dict['sumTransactAmount']    = row.SumTransactAmount
        column_dict['transactionCount']     = row.TransactionCount
        
        row_list.append(column_dict)
    
    return row_list

def query_redemption_monthly_by_outlet(outlet, month, year):
    date_range_start    = datetime(year, month, 1)
    date_range_end      = datetime(year, month, date_util.last_day_of_month(date_range_start).day)
    
    bg_client           = create_bigquery_client(credential_filepath=conf.BIGQUERY_SERVICE_CREDENTIAL_PATH)
    
    db_client = create_db_client(caller_info="query_reward_monthly_by_outlet")
    with db_client.context():
        merchant_acct   = outlet.merchant_acct_entity
        account_code    = merchant_acct.account_code
        account_code    = account_code.replace('-','')
        
    if date_range_start and date_range_end:
        date_range_start    = date_to_bigquery_qualified_datetime_str(date_range_start)
        date_range_end      = date_to_bigquery_qualified_datetime_str(date_range_end)
        
        where_condition = "WHERE PartitionDateTime BETWEEN DATETIME('{date_range_start}') and DATETIME('{date_range_end}') and TransactOutlet='{transact_outlet}'".format(date_range_start=date_range_start,date_range_end=date_range_end, transact_outlet = outlet.key_in_str)
        
    dataset = '%s_%s' % (MERCHANT_DATASET,account_code)
        
    query = '''
        SELECT FORMAT_DATETIME('%Y-%m-%d', RedeemedDateTime) as RedeemedDate, RewardFormat, VoucherKey, sum(TotalRedeemedAmount) as SumRedeemedAmount, count(transactionId) as TransactionCount
        FROM (
        
            SELECT transactionId, RedeemedDateTime, RewardFormat, VoucherKey, SUM(RedeemedAmount) as TotalRedeemedAmount
                    FROM (
                        
                        SELECT
                            checking_transaction.RedeemedDateTime as RedeemedDateTime, 
                            checking_transaction.TransactionId as TransactionId, 
                            checking_transaction.UpdatedDateTime, 
                            checking_transaction.RewardFormat as RewardFormat,
                            checking_transaction.VoucherKey as VoucherKey,
                            checking_transaction.RedeemedAmount as RedeemedAmount,
                            checking_transaction.Reverted as Reverted
                            
                          FROM
                            (
                            SELECT
                               TransactionId, MAX(UpdatedDateTime) AS latestUpdatedDateTime
                             FROM
                               `{project_id}.{dataset_name}.customer_redemption`
                                
                                {where_condition}
                        
                             GROUP BY
                               TransactionId
                               ) 
                               AS latest_transaction
                          INNER JOIN
                          (
                            SELECT DISTINCT 
                            RedeemedDateTime, TransactionId, UpdatedDateTime, RewardFormat, VoucherKey, RedeemedAmount, Reverted
                            FROM
                            `{project_id}.{dataset_name}.customer_redemption`
                              
                              {where_condition}
                        
                          ) as checking_transaction
                        
                        ON
                        
                        checking_transaction.TransactionId = latest_transaction.TransactionId
                        AND
                        checking_transaction.UpdatedDateTime=latest_transaction.latestUpdatedDateTime
                        
                )
                WHERE Reverted=False
                GROUP BY transactionId, RedeemedDateTime, RewardFormat, VoucherKey
        )
        GROUP BY RedeemedDate, RewardFormat, VoucherKey    
        order by RedeemedDate        
        '''.format(project_id=BIGQUERY_GCLOUD_PROJECT_ID, dataset_name=dataset, where_condition=where_condition, account_code=account_code) 
    
    logger.debug('query=%s', query);
        
    try:
        
        job_result_rows = execute_query(bg_client, query)
    except:
        job_result_rows = []
        logger.error('Failed to execute query due to %s', get_tracelog())
    
    
    row_list = []
    for row in job_result_rows:
        #logger.debug(row)
        column_dict = {}
        column_dict['redeemedDate']         = row.RedeemedDate
        column_dict['rewardFormat']         = row.RewardFormat
        column_dict['voucherKey']           = row.VoucherKey
        column_dict['sumRedeemedAmount']    = row.SumRedeemedAmount
        column_dict['transactionCount']     = row.TransactionCount
        
        row_list.append(column_dict)
    
    return row_list
    
def query_partnership_transaction_monthly_by_partner_merchant(merchant_acct, partner_merchant_acct, month, year):
    date_range_start    = datetime(year, month, 1)
    date_range_end      = datetime(year, month, date_util.last_day_of_month(date_range_start).day)
    
    bg_client       = create_bigquery_client(credential_filepath=conf.BIGQUERY_SERVICE_CREDENTIAL_PATH)
    
    db_client = create_db_client(caller_info="query_partnership_transaction_monthly_by_outlet")
    with db_client.context():
        account_code    = merchant_acct.account_code
        account_code    = account_code.replace('-','')
    
    partner_merchant_acct_key = partner_merchant_acct.key_in_str
        
    if date_range_start and date_range_end:
        date_range_start    = date_to_bigquery_qualified_datetime_str(date_range_start)
        date_range_end      = date_to_bigquery_qualified_datetime_str(date_range_end)
        
        where_condition = "WHERE PartitionDateTime BETWEEN DATETIME('{date_range_start}') and DATETIME('{date_range_end}') and PartnerMerchantKey='{partner_merchant_acct_key}'".format(date_range_start=date_range_start,date_range_end=date_range_end, partner_merchant_acct_key = partner_merchant_acct_key)
        
    dataset = '%s_%s' % (MERCHANT_DATASET,account_code)
        
    query = '''
        SELECT TransactDate,  
                sum(TotalTransactPointAmount) as SumTotalTransactPointAmount, count(transactionId) as TransactionCount
        FROM (
        
            SELECT TransactionId, DATE(TransactDateTime) as TransactDate, SUM(TransactPointAmount) as TotalTransactPointAmount
                    FROM (
                        
                        SELECT
                            checking_transaction.TransactDatetime as TransactDatetime, 
                            checking_transaction.TransactionId as TransactionId, 
                            checking_transaction.UpdatedDateTime, 
                            checking_transaction.TransactPointAmount as TransactPointAmount,
                            
                            
                          FROM
                            (
                            SELECT
                               TransactionId, MAX(UpdatedDateTime) AS latestUpdatedDateTime
                             FROM
                               `{project_id}.{dataset_name}.partnership_reward_transaction`
                                
                                {where_condition}
                        
                             GROUP BY
                               TransactionId
                               ) 
                               AS latest_transaction
                          INNER JOIN
                          (
                            SELECT 
                            TransactDateTime, TransactionId, UpdatedDateTime, TransactPointAmount
                            FROM
                            `{project_id}.{dataset_name}.partnership_reward_transaction`
                              
                              {where_condition}
                        
                          ) as checking_transaction
                        
                        ON
                        
                        checking_transaction.TransactionId = latest_transaction.TransactionId
                        AND
                        checking_transaction.UpdatedDateTime=latest_transaction.latestUpdatedDateTime
                        
                )
                GROUP BY TransactionId, TransactDateTime
        )
        GROUP BY TransactDate    
        order by TransactDate        
        '''.format(project_id=BIGQUERY_GCLOUD_PROJECT_ID, dataset_name=dataset, where_condition=where_condition, account_code=account_code) 
    
    query_new = '''
        SELECT TransactDate,  
                sum(TotalTransactPointAmount) as SumTotalTransactPointAmount, count(transactionId) as TransactionCount
        FROM (
        
            SELECT TransactionId, DATE(TransactDateTime) as TransactDate, SUM(TransactPointAmount) as TotalTransactPointAmount
                FROM 
                   `{project_id}.{dataset_name}.partnership_reward_transaction`
                    
                    {where_condition}
                GROUP BY TransactionId, TransactDate
        )
        GROUP BY TransactDate    
        order by TransactDate        
        '''.format(project_id=BIGQUERY_GCLOUD_PROJECT_ID, dataset_name=dataset, where_condition=where_condition, account_code=account_code)
    
    logger.debug('query=%s', query_new);
    
    
    try:
        
        job_result_rows = execute_query(bg_client, query_new)
    except:
        job_result_rows = []
        logger.error('Failed to execute query due to %s', get_tracelog())
    
    
    row_list = []
    for row in job_result_rows:
        #logger.debug(row)
        column_dict = {}
        column_dict['TransactDate']                 = row.TransactDate
        column_dict['SumTotalTransactPointAmount']  = row.SumTotalTransactPointAmount
        column_dict['TransactionCount']             = row.TransactionCount
        
        row_list.append(column_dict)
    
    return row_list    


def query_outlet_sales_monthly_by_transact_date(outlet, month, year):
    date_range_start    = datetime(year, month, 1)
    date_range_end      = datetime(year, month, date_util.last_day_of_month(date_range_start).day)
    
    bg_client       = create_bigquery_client(credential_filepath=conf.BIGQUERY_SERVICE_CREDENTIAL_PATH)
    
    db_client = create_db_client(caller_info="query_outlet_sales_monthly")
    with db_client.context():
        merchant_acct   = outlet.merchant_acct_entity
        account_code    = merchant_acct.account_code
        account_code    = account_code.replace('-','')
        
    if date_range_start and date_range_end:
        date_range_start    = date_to_bigquery_qualified_datetime_str(date_range_start)
        date_range_end      = date_to_bigquery_qualified_datetime_str(date_range_end)
        
        where_condition = "WHERE PartitionDateTime BETWEEN DATETIME('{date_range_start}') and DATETIME('{date_range_end}') and TransactOutlet='{transact_outlet}'".format(date_range_start=date_range_start,date_range_end=date_range_end, transact_outlet = outlet.key_in_str)
        
    dataset = '%s_%s' % (MERCHANT_DATASET,account_code)
        
    query = '''
        
        
            SELECT 
            FORMAT_DATETIME('%Y-%m-%d', TransactDateTime) as TransactDate, 
            FORMAT("%.2f", SUM(TransactAmount)) as TotalTransactAmount

            
                    FROM (
                        
                        SELECT
                            checking_transaction.TransactDateTime as TransactDateTime,
                            checking_transaction.TransactionId as TransactionId, 
                            checking_transaction.UpdatedDateTime, 
                            checking_transaction.TransactAmount as TransactAmount,
                            checking_transaction.Reverted as Reverted
                            
                          FROM
                            (
                            SELECT
                               TransactionId, MAX(UpdatedDateTime) AS latestUpdatedDateTime
                             FROM
                               `{project_id}.{dataset_name}.sales_transaction`
                                
                                {where_condition}
                        
                             GROUP BY
                               TransactionId
                               ) 
                               AS latest_transaction
                          INNER JOIN
                          (
                            SELECT 
                            TransactDateTime, TransactionId, UpdatedDateTime, TransactAmount, Reverted
                            FROM
                            `{project_id}.{dataset_name}.sales_transaction`
                              
                              {where_condition}
                        
                          ) as checking_transaction
                        
                        ON
                        
                        checking_transaction.TransactionId = latest_transaction.TransactionId
                        AND
                        checking_transaction.UpdatedDateTime=latest_transaction.latestUpdatedDateTime
                        
                )
                WHERE Reverted=False
                GROUP BY TransactDate
            order by TransactDate
        '''.format(project_id=BIGQUERY_GCLOUD_PROJECT_ID, dataset_name=dataset, where_condition=where_condition, account_code=account_code)
    
    query_new = '''
        SELECT
            FORMAT_DATETIME('%Y-%m-%d', TransactDateTime) as TransactDate, 
            FORMAT("%.2f", SUM(TransactAmount)) as TotalTransactAmount
            FROM (
                SELECT
                  TransactDateTime,
                  TransactionId,
                  TransactAmount,
                  Reverted,
                  UpdatedDateTime
                FROM (
                
                SELECT
                  TransactDateTime,
                  TransactionId,
                  TransactAmount,
                  Reverted,
                  UpdatedDateTime,
                  FIRST_VALUE(Reverted) OVER (PARTITION BY TransactionId ORDER BY UpdatedDateTime DESC) AS latest_status
                FROM `{project_id}.{dataset_name}.sales_transaction`
                {where_condition}
                )
                WHERE latest_status=False
                ) GROUP BY TransactDateTime
    
    '''.format(project_id=BIGQUERY_GCLOUD_PROJECT_ID, dataset_name=dataset, where_condition=where_condition, account_code=account_code)
        
    logger.debug('query=%s', query_new);
    
    try:
        
        job_result_rows = execute_query(bg_client, query_new)
    except:
        job_result_rows = []
        logger.error('Failed to execute query due to %s', get_tracelog())
    
    
    row_list = []
    for row in job_result_rows:
        #logger.debug(row)
        column_dict = {}
        column_dict['TransactDate']         = row.TransactDate
        #column_dict['TransactionId']        = row.TransactionId
        column_dict['TotalTransactAmount']  = float(row.TotalTransactAmount)
        
        
        row_list.append(column_dict)
    
    return row_list

def query_sales_monthly_by_outlet(merchant_acct, month, year):
    date_range_start    = datetime(year, month, 1)
    date_range_end      = datetime(year, month, date_util.last_day_of_month(date_range_start).day)
    
    bg_client       = create_bigquery_client(credential_filepath=conf.BIGQUERY_SERVICE_CREDENTIAL_PATH)
    
    db_client = create_db_client(caller_info="query_sales_monthly_by_outlet")
    with db_client.context():
        account_code    = merchant_acct.account_code
        account_code    = account_code.replace('-','')
        
    if date_range_start and date_range_end:
        date_range_start    = date_to_bigquery_qualified_datetime_str(date_range_start)
        date_range_end      = date_to_bigquery_qualified_datetime_str(date_range_end)
        
        where_condition = "WHERE PartitionDateTime BETWEEN DATETIME('{date_range_start}') and DATETIME('{date_range_end}')".format(date_range_start=date_range_start,date_range_end=date_range_end, )
        
    dataset = '%s_%s' % (MERCHANT_DATASET,account_code)
        
    query = '''
        
        
            SELECT 
            TransactOutlet, 
            FORMAT("%.2f", SUM(TransactAmount)) as TotalTransactAmount

            
                    FROM (
                        
                        SELECT
                            checking_transaction.TransactOutlet as TransactOutlet, 
                            checking_transaction.TransactionId as TransactionId, 
                            checking_transaction.UpdatedDateTime, 
                            checking_transaction.TransactAmount as TransactAmount,
                            checking_transaction.Reverted as Reverted
                            
                          FROM
                            (
                            SELECT
                               TransactionId, MAX(UpdatedDateTime) AS latestUpdatedDateTime
                             FROM
                               `{project_id}.{dataset_name}.sales_transaction`
                                
                                {where_condition}
                        
                             GROUP BY
                               TransactionId
                               ) 
                               AS latest_transaction
                          INNER JOIN
                          (
                            SELECT 
                            TransactOutlet, TransactionId, UpdatedDateTime, TransactAmount, Reverted
                            FROM
                            `{project_id}.{dataset_name}.sales_transaction`
                              
                              {where_condition}
                        
                          ) as checking_transaction
                        
                        ON
                        
                        checking_transaction.TransactionId = latest_transaction.TransactionId
                        AND
                        checking_transaction.UpdatedDateTime=latest_transaction.latestUpdatedDateTime
                        
                )
                WHERE Reverted=False
                GROUP BY TransactOutlet
        
                
        '''.format(project_id=BIGQUERY_GCLOUD_PROJECT_ID, dataset_name=dataset, where_condition=where_condition, account_code=account_code) 
    
    query_new = '''
        SELECT
            TransactOutlet, 
            FORMAT("%.2f", SUM(TransactAmount)) as TotalTransactAmount
            FROM (
                SELECT
                  TransactDateTime,
                  TransactionId,
                  TransactAmount,
                  Reverted,
                  UpdatedDateTime
                FROM (
                
                SELECT
                  TransactDateTime,
                  TransactionId,
                  TransactAmount,
                  Reverted,
                  UpdatedDateTime,
                  FIRST_VALUE(Reverted) OVER (PARTITION BY TransactionId ORDER BY UpdatedDateTime DESC) AS latest_status
                FROM `{project_id}.{dataset_name}.sales_transaction`
                {where_condition}
                )
                WHERE latest_status=False
                ) GROUP BY TransactOutlet
    
    '''.format(project_id=BIGQUERY_GCLOUD_PROJECT_ID, dataset_name=dataset, where_condition=where_condition, account_code=account_code)
        
    logger.debug('query=%s', query_new);
        
    #logger.debug('query=%s', query);
    
    try:
        
        job_result_rows = execute_query(bg_client, query_new)
    except:
        job_result_rows = []
        logger.error('Failed to execute query due to %s', get_tracelog())
    
    
    row_list = []
    for row in job_result_rows:
        #logger.debug(row)
        column_dict = {}
        column_dict['TransactOutlet']         = row.TransactOutlet
        column_dict['TotalTransactAmount']  = float(row.TotalTransactAmount)
        
        
        row_list.append(column_dict)
    
    return row_list