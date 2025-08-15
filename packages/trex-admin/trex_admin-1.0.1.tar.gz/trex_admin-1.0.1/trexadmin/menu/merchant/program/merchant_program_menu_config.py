'''
Created on 18 Sep 2023

@author: jacklok
'''
from flask_babel import gettext
from trexadmin.menu.merchant.program.merchant_membership_menu_config import manage_membership_sub_menu
from trexadmin.menu.merchant.program.merchant_reward_program_menu_config import manage_reward_program_sub_menu
from trexadmin.menu.merchant.program.merchant_redeem_program_menu_config import manage_redeem_program_sub_menu

voucher_setup_menu_item = {
                                    'title'             : gettext('Voucher'),
                                    'menu_item'         : 'voucher_setup_voucher_overview',
                                    'end_point'         : 'voucher_setup_bp.voucher_overview',
                                    'icon_class'        : 'fas fa-ticket',
                                    'permission'        : 'manage_loyalty_program',
                                    'loyalty_package'   : ['lite', 'standard', 'scale'],
                        
                        }





prepaid_cash_setup_menu_item = {
                                    'title'             : gettext('Prepaid Cash'),
                                    'menu_item'         : 'manage_prepaid_program',
                                    'icon_class'        : 'fas fa-cog',
                                    'end_point'         : 'prepaid_setup_bp.manage_prepaid',
                                    'permission'        : 'manage_prepaid_program',
                                    'loyalty_package'   : ['scale'],
                        
                        }

prepaid_redeem_settings_menu_item = {
                                    'title'             : gettext('Prepaid Redeem Code'),
                                    'menu_item'         : 'manage_prepaid_redeem_settings',
                                    'icon_class'        : 'fas fa-cog',
                                    'end_point'         : 'prepaid_redeem_settings_bp.search_prepaid_redeem_settings',
                                    'permission'        : 'manage_prepaid_redeem_settings',
                                    'loyalty_package'   : ['scale'],
                        
                        }

prepaid_program_sub_menu = {
                                    'title'             : gettext('Prepaid Program'),
                                    'menu_item'         : 'manage_prepaid',
                                    'icon_class'        : 'fas fa-usd',
                                    'permission'        : 'manage_prepaid',
                                    'loyalty_package'   : ['scale'],
                                    'childs'        : [
                                    
                                                    prepaid_cash_setup_menu_item,
                                                    prepaid_redeem_settings_menu_item,
                                                            
                                                ]
                        
                        }



manage_program_settings_menu_item = {
                                    'title'         : gettext('Other Settings'),
                                    'menu_item'     : 'manage_program_settings',
                                    'icon_class'    : 'fas fa-cogs',
                                    'permission'    : 'manage_loyalty_program',
                                    'end_point'     : 'manage_program_settings_bp.manage_program_settings',
                        
                        }



program_device_setup_sub_menu = {
                        'title'         : gettext('Program Device'),
                        'menu_item'     : 'merchant_loyalty_device_setup',
                        'end_point'     : 'loyalty_device_setup_bp.loyalty_device_search',
                        'icon_class'    : 'fas fa-cog',
                        'permission'    : 'manage_loyalty_program',
                        
                        }

lucky_draw_program_setup_menu_item = {
                                    'title'             : gettext('Scrach to Win'),
                                    'menu_item'         : 'lucky_draw_program_listing',
                                    'end_point'         : 'lucky_draw_program_bp.lucky_draw_program_listing',
                                    'icon_class'        : 'fas fa-cog',
                                    'permission'        : 'manage_loyalty_program',
                                    'loyalty_package'   : ['scale'],
                        
                        }

lucky_draw_program_settings_menu_item = {
                                    'title'             : gettext('Scheme Settings'),
                                    'menu_item'         : 'lucky_draw_program_settings',
                                    'end_point'         : 'lucky_draw_program_settings_bp.lucky_draw_program_settings',
                                    'icon_class'        : 'fas fa-cog',
                                    'permission'        : 'manage_loyalty_program',
                                    'loyalty_package'   : ['scale'],
                        
                        }

lucky_draw_thru_app_program_sub_menu = {
                                    'title'             : gettext('Draw Thru App'),
                                    'menu_item'         : 'lucky_draw_program_listing',
                                    'icon_class'        : 'fas fa-mobile',
                                    'permission'        : 'manage_loyalty_program',
                                    'loyalty_package'   : ['scale'],
                                    'childs'        : [
                                    
                                                    lucky_draw_program_setup_menu_item,
                                                    lucky_draw_program_settings_menu_item,
                                                            
                                                ]
                        
                        }

lucky_draw_program_sub_menu = {
                                    'title'             : gettext('Lucky Draw Program'),
                                    'menu_item'         : 'lucky_draw_program_listing',
                                    'icon_class'        : 'fas fa-dice',
                                    'permission'        : 'manage_loyalty_program',
                                    'loyalty_package'   : ['scale'],
                                    'childs'        : [
                                    
                                                    lucky_draw_thru_app_program_sub_menu,
                                                            
                                                ]
                        
                        }




referral_program_setup_menu_item = {
                                    'title'             : gettext('Program Setup'),
                                    'menu_item'         : 'referral_program_listing',
                                    'end_point'         : 'referral_program_setup_bp.referral_programs_listing',
                                    'icon_class'        : 'fas fa-cog',
                                    'permission'        : 'manage_loyalty_program',
                                    'loyalty_package'   : ['scale'],
                        
                        }

referrer_program_promote_text_menu_item = {
                                    'title'             : gettext('Referrer Promote Text'),
                                    'menu_item'         : 'referral_program_listing',
                                    'end_point'         : 'referral_program_settings_bp.show_program_referrer_promote_text',
                                    'icon_class'        : 'fas fa-cog',
                                    'permission'        : 'manage_loyalty_program',
                                    'loyalty_package'   : ['scale'],
                        
                        }

referee_program_promote_text_menu_item = {
                                    'title'             : gettext('Referee Promote Text'),
                                    'menu_item'         : 'referral_program_listing',
                                    'end_point'         : 'referral_program_settings_bp.show_program_referee_promote_text',
                                    'icon_class'        : 'fas fa-cog',
                                    'permission'        : 'manage_loyalty_program',
                                    'loyalty_package'   : ['scale'],
                        
                        }

referrer_program_promote_image_menu_item = {
                                    'title'             : gettext('Referrer Promote Image'),
                                    'menu_item'         : 'referral_program_listing',
                                    'end_point'         : 'referral_program_settings_bp.show_program_referrer_promote_image',
                                    'icon_class'        : 'fas fa-cog',
                                    'permission'        : 'manage_loyalty_program',
                                    'loyalty_package'   : ['scale'],
                        
                        }

referee_program_promote_image_menu_item = {
                                    'title'             : gettext('Referee Promote Image'),
                                    'menu_item'         : 'referee_program_listing',
                                    'end_point'         : 'referral_program_settings_bp.show_program_referee_promote_image',
                                    'icon_class'        : 'fas fa-cog',
                                    'permission'        : 'manage_loyalty_program',
                                    'loyalty_package'   : ['scale'],
                        
                        }



referral_program_sub_menu = {
                                    'title'             : gettext('Referral Program'),
                                    'menu_item'         : 'referral_program_group',
                                    'icon_class'        : 'fas fa-id-badge',
                                    'permission'        : 'manage_referral_program',
                                    'loyalty_package'   : ['scale'],
                                    'childs'        : [
                                    
                                                    referral_program_setup_menu_item,
                                                    referrer_program_promote_text_menu_item,
                                                    referee_program_promote_text_menu_item,
                                                    referrer_program_promote_image_menu_item,
                                                    referee_program_promote_image_menu_item,
                                                            
                                                ]
                        
                        }


menu_items = {
                                
                                'title'         : gettext('Program'),
                                'menu_item'     : 'reward_program',
                                'icon_class'    : 'fas fa-diamond',
                                'product_code'  : 'loyalty',
                                'permission'    : ['manage_loyalty_program'],
                                'childs'        : [
                                                    manage_membership_sub_menu,
                                                    voucher_setup_menu_item,
                                                    manage_reward_program_sub_menu,
                                                    manage_redeem_program_sub_menu,
                                                    prepaid_program_sub_menu,
                                                    lucky_draw_program_sub_menu,
                                                    referral_program_sub_menu,
                                                    #manage_program_settings_menu_item,
                                                    program_device_setup_sub_menu,
                                                    
                                                            
                                                ]
                }