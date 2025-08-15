'''
Created on 6 May 2025

@author: jacklok
'''
from flask_babel import gettext

merchant_partnership_setup_menu_item = {
                                    'title'             : gettext('Setup'),
                                    'menu_item'         : 'merchant_partnership',
                                    'end_point'         : 'merchant_manage_partnership_setup_bp.merchant_partnership_setup',
                                    'icon_class'        : 'fas fa-plus-circle',
                                    'permission'        : 'merchant_partnership_setup',

                        
                        }

merchant_partnership_settings_menu_item = {
                                    'title'             : gettext('Settings'),
                                    'menu_item'         : 'merchant_partnership_settings',
                                    'end_point'         : 'merchant_partnership_settings_bp.merchant_partnership_settings',
                                    'icon_class'        : 'fas fa-cogs',
                                    'permission'        : 'merchant_partnership_settings',

                        
                        }

menu_items = {
                                    'title'         : gettext('Partnership'),
                                    'menu_item'     : 'marketing',
                                    'icon_class'    : 'fas fa-handshake',
                                    'permission'    : 'partnership',
                                    'loyalty_package'   : ['scale'],
                                    'childs'        : [
                                                        merchant_partnership_settings_menu_item,
                                                        merchant_partnership_setup_menu_item,
                                                        
                                                        ]
                        
                        }