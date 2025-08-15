'''
Created on 28 Apr 2021

@author: jacklok
'''

import os

SYSTEM_BASE_URL     = os.environ.get('SYSTEM_BASE_URL')


def task_url(path):
    return '{}{}'.format(SYSTEM_BASE_URL, path)

CHECK_CUSTOMER_ENTITLE_REWARD_TASK_URL  = task_url('/rewarding/check-entitle-reward')
SEND_EMAIL_TASK_URL                     = task_url('/system/send-email')

