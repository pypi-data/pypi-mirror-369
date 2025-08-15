'''
Created on 17 Dec 2020

@author: jacklok
'''

report_joined_merchant_sub_menu = {
                        'title'         : 'Joined Merchant',
                        'menu_item'     : 'joined_merchant',
                        'end_point'     : 'admin_merchant_report_bp.joined_merchant_report',
                        'icon_class'    : 'fas fa-table',
                        'permission'    : 'read_admin_report',
                        }

report_merchant_transaction_sub_menu = {
                        'title'         : 'Merchant Transaction',
                        'menu_item'     : 'merchant_transaction',
                        'end_point'     : 'admin_merchant_report_bp.merchant_transaction_report',
                        'icon_class'    : 'fas fa-table',
                        'permission'    : 'read_admin_report',
                        }

admin_report_merchant_module_menu = {
                                        'title'         : 'Merchant Report',
                                        'menu_item'     : 'merchant_report',
                                        'icon_class'    : 'fas fa-database',
                                        'permission'    : 'read_admin_report',
                                        'childs'        : [
                                                            report_joined_merchant_sub_menu,
                                                            report_merchant_transaction_sub_menu,
                                                        ]
                                        }

menu_items     = {
                                    
                        'title'         : 'Report',
                        'menu_item'     : 'report',
                        'icon_class'    : 'fas fa-database',
                        'permission'    : 'read_admin_report',
                        'childs'        : [
                                            admin_report_merchant_module_menu
                                            
                                            ]
                    }

