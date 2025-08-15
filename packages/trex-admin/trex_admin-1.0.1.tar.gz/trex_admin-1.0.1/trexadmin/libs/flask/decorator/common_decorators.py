'''
Created on 5 May 2020

@author: jacklok
'''

from functools import wraps
from flask import request, abort
import logging

logger = logging.getLogger("debug")

def page_title(title=None):
    def decorator(fn):
        @wraps(fn)
        def decorated_function(*args, **kwargs):
            ctx = fn(*args, **kwargs)
            
            logging.debug('page title=%s', title)
            if ctx:
                
                kwargs['page_title'] = title
            logging.debug('args=%s', args)
            logging.debug('kwargs=%s', kwargs)
            return ctx
        return decorated_function
    return decorator

def limit_content_length(max_length):
    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            cl = request.content_length
            logger.debug('content length=%s and max_length=%s, and cl > max_length=%s', cl, max_length, cl > max_length)
            
            if cl is not None and cl > max_length:
                logger.debug('File too large')
                abort(413)
            logger.debug('File size is acceptable')
            logger.debug('*args=%s', args)
            logger.debug('**kwargs=%s', kwargs)
            return f(*args, **kwargs)
        return wrapper
    return decorator



