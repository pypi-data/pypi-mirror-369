'''
Created on 18 Sep 2023

@author: jacklok
'''
from flask_babel import gettext


manage_basic_membership_menu_item = {
                                    'title'             : gettext('Basic Membership'),
                                    'menu_item'         : 'manage_basic_membership_overview',
                                    'end_point'         : 'merchant_manage_basic_membership_bp.basic_membership_overview',
                                    'icon_class'        : 'fas fa-user',
                                    'permission'        : 'manage_membership',
                                    'loyalty_package'   : ['lite','standard','scale'],
                        
                        }

manage_tier_membership_menu_item = {
                                    'title'             : gettext('Tier Membership'),
                                    'menu_item'         : 'manage_tier_membership_overview',
                                    'end_point'         : 'merchant_manage_tier_membership_bp.tier_membership_overview',
                                    'icon_class'        : 'fas fa-id-badge',
                                    'permission'        : 'manage_membership',
                                    'loyalty_package'   : ['scale'],
                        
                        }

manage_membership_sub_menu = {
                                    'title'         : gettext('Membership'),
                                    'menu_item'     : 'manage_membership_overview',
                                    'icon_class'    : 'fas fa-id-card-clip',
                                    'permission'    : 'manage_membership',
                                    'loyalty_package'   : ['lite','standard','scale'],
                                    'childs'        : [
                                    
                                                    manage_basic_membership_menu_item,
                                                    manage_tier_membership_menu_item,
                                                            
                                                ]
                        
                        }