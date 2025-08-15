'''
Created on 4 Jan 2021

@author: jacklok
'''
from flask_babel import gettext

merchant_manage_promotion_code_sub_menu = {
                        'title'         : gettext('Code'),
                        'menu_item'     : 'manage_promotion_code',
                        'end_point'     : 'merchant_manage_promotion_code_bp.merchant_promotion_code',
                        'icon_class'    : 'fas fa-code',
                        'permission'    : 'manage_promotion',
                        
                        }


menu_items = {
                                'title'         : 'Promotion',
                                'menu_item'     : 'crm',
                                'icon_class'    : 'fas fa-percent',
                                'permission'    : ['manage_promotion'],
                                'childs'        : [
                                    
                                                    merchant_manage_promotion_code_sub_menu,
                                                    
                                                            
                                                ]
                }


