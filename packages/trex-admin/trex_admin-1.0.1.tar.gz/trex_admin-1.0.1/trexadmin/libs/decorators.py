'''
Created on Jan 22, 2012

@author: lokjac
'''
from functools import wraps
from trexlib.utils.url_util import base64_url_encode  

import traceback, logging
import hashlib
from trexadmin.libs.http import StatusCode 
from trexlib.utils.string_util import str_to_bool, resolve_unicode_value
from trexlib.utils.log_util import get_tracelog
import types


logger = logging.getLogger('lib')

def http_debug(debug=False):
    def wrapper(fn):
        def http_debug_wrapper(*args, **kwargs):
            handler     = args[0]
            request     = handler.request
            show_debug  = str_to_bool(request.headers.get('X-http-debug'))
            if show_debug or debug:
                logger.debug('\n\n================== start: debug http request ====================')
                for key in request.headers:
                    logging.debug('%s = %s', key, request.headers.get(key))

                logger.debug('\n================== end: debug http request ====================\n\n')

            return fn(*args, **kwargs)

        return http_debug_wrapper
    return wrapper


def hooked_model_class(original_class): #decorator
    original_put    = original_class.put

    def put(self, **kwargs):
        logging.debug('---hooked_model_class(%s)---', original_class)

        pre_func = getattr(self, 'before_put', None)
        #logging.debug('getting hooked before_put_func=%s', pre_func)

        if callable(pre_func):
            pre_func()
            logging.debug('called pre_func')

        try:
            original_put(self, **kwargs)

            post_func = getattr(self, 'after_put', None)

            #logging.debug('getting hooked after_put_func=%s', post_func)
            if callable(post_func):
                post_func()
                logging.debug('called post_func')
        except:
            logger.debug('ignore post function due to error=%s', get_tracelog())
            #raise

    original_class.put = put
    return original_class

def elapsed_time_trace(debug=False, trace_key=None):
    def wrapper(fn):
        import time
        def elapsed_time_trace_wrapper(*args, **kwargs):
            start = time.time()
            result      = fn(*args, **kwargs)
            end = time.time()
            elapsed_time = end - start
            trace_name      = trace_key or fn.func_name
            first_argument  = args[0] if args else None
            logger.info('==================== Start Elapsed Time Trace %s(%s) ===========================', trace_name, first_argument)
            logger.info('elapsed time=%s', ("%.2gs" % (elapsed_time)))
            logger.info('================================================================================')
            return result

        return elapsed_time_trace_wrapper
    return wrapper

def _add_hook_for(cls, target):
    def hook_decorator(hook):
        def hooked(s, *p, **k):
            ret = target(s, *p, **k)
            # some magic happens here
            logger.debug('applied hook here')
            logger.debug('hook_decorator: %s', hook(s, *p, **k))
            return ret
        setattr(cls, target.__name__, hooked)
        return hook
    return hook_decorator

def unicode_decode_deco(cls):
    @_add_hook_for(cls, cls.put)
    def before_put(s, *p, **k):
        return 'before put to %s' % cls.__name__

    return cls

