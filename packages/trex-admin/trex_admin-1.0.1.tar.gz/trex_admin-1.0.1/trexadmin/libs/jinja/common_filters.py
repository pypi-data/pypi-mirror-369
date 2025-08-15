'''
Created on 19 May 2020

@author: jacklok
'''
import logging
from trexconf import conf as lib_conf
from trexlib.utils.common.date_util import increase_date
from six import string_types
from datetime import datetime, date
from trexlib.utils.string_util import is_empty
from trexlib.utils.common.currency_util import format_currency as currency_formatting
from trexconf.conf import DEFAULT_GMT_HOURS
from _datetime import timedelta

#logger = logging.getLogger('utils')
logger = logging.getLogger('debug')

def is_date_expired_filter(date_value, date_format='%d-%m-%Y'):
    if isinstance(date_value, string_types):
        date_value = datetime.strptime(date_value, date_format)
    
    today = datetime.utcnow()
    return today>date_value 
    
    

def gmt_datetime(datetime_value, gmt=lib_conf.DEFAULT_GMT):
    if datetime_value:
        new_gmt_datetime = increase_date(datetime_value, hour=gmt)

        return new_gmt_datetime
        
    else:
        return ''

def pretty_datetime_filter(context, datetime_value, datetime_format=None, show_datetime_format=None, gmt_hour=DEFAULT_GMT_HOURS):
    logger.debug('pretty_datetime_filter: datetime_value=%s', datetime_value)
     
    if datetime_format is None:
        datetime_format = '%d/%m/%Y %H:%M:%S'
        
         
     
    if isinstance(datetime_value, string_types):
        datetime_value = datetime.strptime(datetime_value, datetime_format)
        
        if datetime_value:
            datetime_value +=timedelta(hours=gmt_hour)
            if show_datetime_format is None:
                show_datetime_format = '%d %b %Y %I:%M:%S %p'
            return datetime_value.strftime(show_datetime_format)
    elif isinstance(datetime_value, datetime):
        datetime_value +=timedelta(hours=gmt_hour)
        if show_datetime_format is None:
            show_datetime_format = '%d %b %Y %I:%M:%S %p'
        return datetime_value.strftime(show_datetime_format)
    else:
        datetime_value

def format_percentage_filter(value_2_format, currency_details=None):
    return currency_formatting(value_2_format,
                        floating_point          = 2,
                        decimal_separator       = currency_details.get('decimal_separator'),
                        thousand_separator      = currency_details.get('thousand_separator'),
                        show_thousand_separator = True,
                        show_currency_label     = False
                        )

def format_numeric_filter(value_2_format, currency_details=None):
    return currency_formatting(value_2_format,
                        floating_point          = currency_details.get('floating_point'),
                        decimal_separator       = currency_details.get('decimal_separator'),
                        thousand_separator      = currency_details.get('thousand_separator'),
                        show_thousand_separator = True,
                        show_currency_label     = False
                        )
    
def format_currency_with_currency_label_filter(value_2_format, currency_details=None):
    return currency_formatting(value_2_format,
                        currency_label          = currency_details.get('currency_label'),
                        floating_point          = currency_details.get('floating_point'),
                        decimal_separator       = currency_details.get('decimal_separator'),
                        thousand_separator      = currency_details.get('thousand_separator'),
                        show_thousand_separator = True,
                        show_currency_label     = True
                        )    
    

def format_integer_filter(value_2_format, currency_details=None):
    return currency_formatting(value_2_format,
                        floating_point          = 0,
                        decimal_separator       = currency_details.get('decimal_separator'),
                        thousand_separator      = currency_details.get('thousand_separator'),
                        show_thousand_separator = True,
                        show_currency_label     = False
                        )   

def pretty_date_filter(context, date_value, date_format=None, pretty_date_format=None):
    
    logger.debug('pretty_date_filter: date_value=%s', date_value)
    logger.debug('pretty_date_filter: date_format=%s', date_format)
    
    if date_format is None:
        date_format = '%d/%m/%Y'
    
    if isinstance(date_value, string_types):
        logger.debug('pretty_date_filter: is string type')
        date_value = datetime.strptime(date_value, date_format)
        if date_value:
            if pretty_date_format:
                return date_value.strftime(pretty_date_format)
            else:
                return date_value.strftime('%d %b %Y')
    elif isinstance(date_value, date):
        logger.debug('pretty_date_filter: is date type')
        if pretty_date_format:
            return date_value.strftime(pretty_date_format)
        else:
            return date_value.strftime('%d %b %Y')
    else:
        logger.debug('pretty_date_filter: unknown type')
         
        return date_value  
    

def standard_date_filter(context, date_value, date_parse_format='%d/%m/%Y', return_date_format="%d/%m/%Y"):
    
    logger.debug('standard_date_filter: date_value=%s', date_value)
    logger.debug('standard_date_filter: date_parse_format=%s', date_parse_format)
    
    if isinstance(date_value, string_types):
        logger.debug('standard_date_filter: date_value is string')
        date_value = datetime.strptime(date_value, date_parse_format)
        
        logger.debug('standard_date_filter: date_value after parsed =%s', date_value)
        
        if date_value:
            return date_value.strftime(return_date_format)
        
    elif isinstance(date_value, date) or isinstance(date_value, datetime):
        logger.debug('standard_date_filter: date_value is date or datetime object')
        return date_value.strftime(return_date_format)
    
        
    return ''

def is_common_member_filter(a, b): 
    logger.debug('is_common_member_filter: a=%s', a)
    logger.debug('is_common_member_filter: b=%s', b)
    if a is not None and b is not None:
        if isinstance(a, str):
            a = [a]
        if isinstance(b, str):
            b = [b]
        
        a_set = set(a) 
        b_set = set(b) 
        if (a_set & b_set): 
            return True 
        else: 
            return False
    else:
        return False

def default_if_empty(value, default_value):
    return_value = value
    try:
        if is_empty(value):
            return_value =  default_value
        
        
    except:
        return_value =  default_value
    
    return return_value
    
def percentage(value):    
    return "%.0f%%" % value

