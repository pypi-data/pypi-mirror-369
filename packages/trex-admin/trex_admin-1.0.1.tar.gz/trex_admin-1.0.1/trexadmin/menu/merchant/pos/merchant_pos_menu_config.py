'''
Created on 25 Aug 2021

@author: jacklok
'''
from flask_babel import gettext

merchant_pos_device_setup_sub_menu = {
                        'title'         : gettext('POS Device'),
                        'menu_item'     : 'merchant_pos_device_setup',
                        'end_point'     : 'pos_device_setup_bp.pos_device_search',
                        'icon_class'    : 'fas fa-cog',
                        'permission'    : 'merchant_pos_device_setup',
                        
                        }

merchant_pos_catalogue_setup_sub_menu = {
                        'title'         : gettext('Assign Catalogue'),
                        'menu_item'     : 'merchant_pos_catalogue_setup',
                        'end_point'     : 'pos_catalogue_setup_bp.pos_catalogue_listing',
                        'icon_class'    : 'fas fa-cog',
                        'permission'    : 'merchant_pos_catalogue_setup',
                        
                        }

dinning_table_setup_sub_menu = {
                        'title'         : gettext('Dinning Table'),
                        'menu_item'     : 'merchant_dinning_table_setup',
                        'end_point'     : 'dining_table_setup_bp.dinning_table_setup_listing',
                        'icon_class'    : 'fas fa-cog',
                        'permission'    : 'merchant_dinning_table_setup',
                        
                        }

dinning_option_sub_menu = {
                        'title'         : gettext('Dinning Option'),
                        'menu_item'     : 'merchant_dinning_option',
                        'end_point'     : 'dinning_option_bp.dinning_option_listing',
                        'icon_class'    : 'fas fa-cog',
                        'permission'    : 'merchant_dinning_option',
                        
                        }

pos_payment_method_sub_menu = {
                        'title'         : gettext('Payment Method'),
                        'menu_item'     : 'merchant_pos_payment_method',
                        'end_point'     : 'pos_payment_method_bp.pos_payment_method_listing',
                        'icon_class'    : 'fas fa-cog',
                        'permission'    : 'merchant_pos_payment_method',
                        
                        }

service_charge_sub_menu = {
                        'title'         : gettext('Additional Charges'),
                        'menu_item'     : 'merchant_pos_service_charge_setup',
                        'end_point'     : 'service_charge_setup_bp.service_charge_setup_listing',
                        'icon_class'    : 'fas fa-cog',
                        'permission'    : 'merchant_pos_service_charge_setup',
                        
                        }

rounding_setup_sub_menu = {
                        'title'         : gettext('Rounding'),
                        'menu_item'     : 'merchant_pos_rounding_setup',
                        'end_point'     : 'rounding_setup_bp.rounding_setup',
                        'icon_class'    : 'fas fa-cog',
                        'permission'    : 'merchant_pos_rounding_setup',
                        
                        }

invoice_no_settings_sub_menu = {
                        'title'         : gettext('Invoice Numbering'),
                        'menu_item'     : 'invoice_no_settings',
                        'end_point'     : 'invoice_no_settings_bp.invoice_no_settings',
                        'icon_class'    : 'fas fa-cog',
                        'permission'    : 'invoice_no_settings',
                        
                        }

service_tax_setup_sub_menu = {
                        'title'         : gettext('Taxes Setup'),
                        'menu_item'     : 'manage_service_tax_setup',
                        'end_point'     : 'service_tax_setup_bp.service_tax_setup_listing',
                        'icon_class'    : 'fas fa-gear',
                        'permission'    : 'manage_service_tax_setup',
                        
                        }

receipt_setup_sub_menu = {
                        'title'         : gettext('Receipt Setup'),
                        'menu_item'     : 'manage_receipt_setup',
                        'end_point'     : 'receipt_setup_bp.receipt_setup',
                        'icon_class'    : 'fas fa-gear',
                        'permission'    : 'manage_receipt_setup',
                        
                        }

menu_items = {
                                'title'         : 'POS',
                                'menu_item'     : 'manage_pos',
                                'icon_class'    : 'fas fa-television',
                                'permission'    : ['merchant_pos_device_setup'],
                                'childs'        : [
                                    
                                                    dinning_option_sub_menu,
                                                    dinning_table_setup_sub_menu,
                                                    merchant_pos_catalogue_setup_sub_menu,
                                                    receipt_setup_sub_menu,
                                                    invoice_no_settings_sub_menu,
                                                    service_tax_setup_sub_menu,
                                                    service_charge_sub_menu,
                                                    rounding_setup_sub_menu,
                                                    pos_payment_method_sub_menu,
                                                    merchant_pos_device_setup_sub_menu,
                                                    
                                                            
                                                ]
                }

'''
pos_setup_submenu_items = {
                                'title'         : 'Setup',
                                'menu_item'     : 'pos_setup',
                                'icon_class'    : 'fas fa-cogs',
                                'permission'    : ['pos_setup'],
                                'childs'        : [
                                    
                                                    dinning_option_sub_menu,
                                                    dinning_table_setup_sub_menu,
                                                    pos_payment_method_sub_menu,
                                                    merchant_pos_catalogue_setup_sub_menu,
                                                    service_charge_sub_menu,
                                                    rounding_setup_sub_menu,
                                                    invoice_no_settings_sub_menu,
                                                    merchant_pos_device_setup_sub_menu,
                                                    
                                                            
                                                ]
                }
'''