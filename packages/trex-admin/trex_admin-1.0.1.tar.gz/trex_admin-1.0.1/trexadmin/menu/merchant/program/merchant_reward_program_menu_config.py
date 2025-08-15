'''
Created on 18 Sep 2023

@author: jacklok
'''
from flask_babel import gettext

reward_program_settings_create_menu_item = {
                                    'title'             : gettext('Basic Program'),
                                    'menu_item'         : 'reward_program_settings_program_index',
                                    'end_point'         : 'reward_program_setup_bp.program_index',
                                    'icon_class'        : 'fas fa-award',
                                    'permission'        : 'reward_program_settings_create_program',
                                    'loyalty_package'   : ['lite','standard','scale'],
                        
                        }


tier_reward_program_menu_item = {
                                    'title'             : gettext('Tier Program'),
                                    'menu_item'         : 'manage_tier_reward_program',
                                    'end_point'         : 'tier_reward_program_setup_bp.manage_tier_reward',
                                    'icon_class'        : 'fas fa-bars',
                                    'permission'        : 'manage_tier_reward_program',
                                    'loyalty_package'   : ['scale'],
                        
                        }

manage_reward_program_sub_menu = {
                                    'title'             : gettext('Reward Program'),
                                    'menu_item'         : 'manage_reward_program',
                                    'icon_class'        : 'fas fa-gifts',
                                    'permission'        : 'manage_reward_program',
                                    'loyalty_package'   : ['lite','standard','scale'],
                                    'childs'        : [
                                    
                                                    reward_program_settings_create_menu_item,
                                                    tier_reward_program_menu_item,
                                                            
                                                ]
                        
                        }