'''
Created on 15 Feb 2022

@author: jacklok
'''
from flask_babel import gettext


merchant_manage_staff_sub_menu = {
                        'title'         : gettext('Manage Staff'),
                        'menu_item'     : 'manage_user',
                        'end_point'     : 'merchant_manage_user_bp.manage_user',
                        'icon_class'    : 'fas fa-user',
                        'permission'    : 'manage_merchant_user',
                        
                        }

menu_items = {
                                'title'         : 'Staff',
                                'menu_item'     : 'merchant_user',
                                'icon_class'    : 'fas fa-users',
                                'permission'    : ['manage_merchant_user'],
                                'childs'        : [
                                    
                                                    merchant_manage_staff_sub_menu,
                                                            
                                                ]
                }