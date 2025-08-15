'''
Created on 19 Jan 2021

@author: jacklok
'''
import os

ANALYTICS_BASE_URL     = os.environ.get('ANALYTICS_BASE_URL')


def data_url(path):
    return '{}{}'.format(ANALYTICS_BASE_URL, path)

ALL_CUSTOMER_GROWTH_CHART_DATA_URL                          = data_url('/analytics/cust/all-cust-growth-by-year-month')

MERCHANT_CUSTOMER_GROWTH_CHART_DATA_URL                     = data_url('/analytics/cust/merchant-cust-growth-by-year-month')
MERCHANT_SALES_GROWTH_CHART_DATA_URL                        = data_url('/analytics/transaction/merchant-transaction-by-date-range')

MERCHANT_CUSTOMER_COUNT_BY_DATE_RANGE_DATA_URL              = data_url('/analytics/cust/merchant-cust-count-by-date-range')
MERCHANT_SALES_AMOUNT_BY_DATE_RANGE_DATA_URL                = data_url('/analytics/sales/merchant-sales-amount-by-date-range')
MERCHANT_TRANSACTION_COUNT_YEARLY_DATE_RANGE_DATA_URL       = data_url('/analytics/transaction/merchant-transaction-total-by-date-range')

MERCHANT_SALES_YEARLY_DATE_RANGE_DATA_URL                   = data_url('/analytics/transaction/merchant-transaction-total-by-date-range')



MERCHANT_CUSTOMER_GENDER_BY_DATE_RANGE_DATA_URL             = data_url('/analytics/cust/merchant-cust-gender-by-date-range')
MERCHANT_CUSTOMER_AGE_GROUP_BY_DATE_RANGE_DATA_URL          = data_url('/analytics/cust/merchant-cust-age-group-by-date-range')