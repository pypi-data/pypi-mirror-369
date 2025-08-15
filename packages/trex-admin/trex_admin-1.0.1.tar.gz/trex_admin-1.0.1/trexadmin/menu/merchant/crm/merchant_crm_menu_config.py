'''
Created on 4 Jan 2021

@author: jacklok
'''
from flask_babel import gettext

merchant_manage_tagging_sub_menu = {
                        'title'         : gettext('Tagging'),
                        'menu_item'     : 'manage_tagging',
                        'end_point'     : 'merchant_settings_tagging_bp.merchant_settings_tagging',
                        'icon_class'    : 'fas fa-tag',
                        'permission'    : 'manage_customer',
                        
                        }


merchant_manage_customer_sub_menu = {
                        'title'         : gettext('Manage Customer'),
                        'menu_item'     : 'manage_customer',
                        'end_point'     : 'merchant_manage_customer_bp.manage_customer',
                        'icon_class'    : 'fas fa-user',
                        'permission'    : 'manage_customer',
                        
                        }

merchant_customer_transaction_sub_menu = {
                        'title'         : gettext('Enter Customer Transaction'),
                        'menu_item'     : 'customer_transaction',
                        'end_point'     : 'merchant_customer_transaction_bp.customer_transaction_search',
                        'icon_class'    : 'fa-dot-circle',
                        'permission'    : 'manage_customer',
                        
                        }




menu_items = {
                                'title'         : 'CRM',
                                'menu_item'     : 'crm',
                                'icon_class'    : 'fas fa-user-circle',
                                'permission'    : ['manage_customer'],
                                'childs'        : [
                                    
                                                    merchant_manage_tagging_sub_menu,
                                                    merchant_manage_customer_sub_menu,
                                                    
                                                            
                                                ]
                }


