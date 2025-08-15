'''
Created on 18 Sep 2023

@author: jacklok
'''

from flask_babel import gettext

redemption_catalogue_menu_item = {
                                    'title'         : gettext('Redemption Catalogue'),
                                    'menu_item'     : 'manage_redemption_catalogue',
                                    'end_point'     : 'redemption_catalogue_bp.manage_redemption_catalogue',
                                    'icon_class'    : 'fas fa-th',
                                    'permission'    : 'manage_redemption_catalogue',
                        
                        }

manage_redeem_program_sub_menu = {
                                    'title'         : gettext('Redeem Program'),
                                    'menu_item'     : 'manage_redeemprogram',
                                    'icon_class'    : 'fas fa-flag',
                                    'permission'    : 'manage_redeem_program',
                                    'childs'        : [
                                    
                                                    redemption_catalogue_menu_item,
                                                            
                                                ]
                        
                        }
