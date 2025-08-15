'''
Created on 5 Jan 2024

@author: jacklok
'''

from flask_babel import gettext
from trexconf import conf

marketing_image_menu_item = {
                                    'title'         : gettext('Marketing Image'),
                                    'menu_item'     : 'manage_marketing_image',
                                    'end_point'     : 'merchant_upload_marketing_image_bp.manage_marketing_image',
                                    'icon_class'    : 'fas fa-file-image',
                                    'permission'    : 'manage_marketing_image',
                        
                        }

push_notification_setup_menu_item = {
                                    'title'         : gettext('Push Notification'),
                                    'menu_item'     : 'manage_push_notification',
                                    'end_point'     : 'push_notification_setup_bp.manage_push_notification_setup',
                                    'icon_class'    : 'fas fa-commenting',
                                    'permission'    : 'manage_push_notification',
                        
                        }

news_setup_menu_item = {
                                    'title'         : gettext('News'),
                                    'menu_item'     : 'manage_news_setup',
                                    'end_point'     : 'merchant_news_setup_bp.manage_merchant_news',
                                    'icon_class'    : 'fas fa-newspaper',
                                    'permission'    : 'manage_news_setup',
                        
                        }

send_message_to_device_menu_item = {
                                    'title'         : gettext('Push to Customer'),
                                    'menu_item'     : 'manage_news_setup',
                                    'end_point'     : 'push_notification_setup_bp.send_message_to_customer',
                                    'icon_class'    : 'fas fa-newspaper',
                                    'permission'    : 'manage_news_setup',
                        
                        }

menu_items_list  = [
                    marketing_image_menu_item,
                    push_notification_setup_menu_item,
                    news_setup_menu_item,
    
                    ]

if conf.IS_LOCAL:
    menu_items_list.append(send_message_to_device_menu_item)

menu_items = {
                                    'title'         : gettext('Marketing'),
                                    'menu_item'     : 'marketing',
                                    'icon_class'    : 'fas fa-flag',
                                    'permission'    : 'marketing',
                                    'childs'        : menu_items_list
                        
                        }