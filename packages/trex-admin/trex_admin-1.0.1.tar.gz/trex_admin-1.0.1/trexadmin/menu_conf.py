'''
Created on 16 Jun 2020

@author: jacklok
'''

manage_admin_sub_menu = {
                        'title'         : 'Manage Administrator Account',
                        'menu_item'     : 'manage_administrator',
                        'end_point'     : 'manage_admin_bp.manage_administrator',
                        'icon_class'    : 'fa-dot-circle',
                        'permission'    : 'manage_admin',
                        }

manage_merchant_sub_menu = {
                        'title'         : 'Manage Merchant Account',
                        'menu_item'     : 'manage_merchant',
                        'end_point'     : 'manage_merchant_bp.manage_merchant',
                        'icon_class'    : 'fa-dot-circle',
                        'permission'    : 'manage_merchant',
                        }

admin_manage_user_sub_menu = {
                        'title'         : 'Manage User Account',
                        'menu_item'     : 'manage_user',
                        'end_point'     : 'admin_manage_user_bp.manage_user',
                        'icon_class'    : 'fa-dot-circle',
                        'permission'    : 'manage_user',
                        }

merchant_manage_user_sub_menu = {
                        'title'         : 'Manage User Account',
                        'menu_item'     : 'manage_user',
                        'end_point'     : 'merchant_manage_user_bp.manage_user',
                        'icon_class'    : 'fa-dot-circle',
                        'permission'    : 'manage_user',
                        
                        }

manage_contact_us_sub_menu = {
                        'title'         : 'Manage Contact Us Listing',
                        'menu_item'     : 'manage_contact_us',
                        'end_point'     : 'manage_contact_us_bp.manage_contact_us_listing',
                        'icon_class'    : 'fa-dot-circle',
                        'permission'    : 'manage_contact_us',
                        }


superuser_settings_module_menu_config = {
                                'title'         : 'Settings',
                                'menu_item'     : 'settings',
                                'icon_class'    : 'fas fa-cogs',
                                'childs'        : [
                                                    manage_admin_sub_menu,
                                                    manage_merchant_sub_menu,  
                                                    manage_contact_us_sub_menu, 
                                                    
                                                           
                                                ]
                            }





merchant_settings_module_menu_config = {
                                'title'         : 'Settings',
                                'menu_item'     : 'settings',
                                'icon_class'    : 'fas fa-cogs',
                                'permission'    : ['manage_user'],
                                'childs'        : [
                                    
                                                    merchant_manage_user_sub_menu
                                                    
                                                            
                                                ]
                            }

payment_module_menu_config = {
                            'title'         : 'Payment',
                            'menu_item'     : 'payment',
                            'icon_class'    : 'fas fa-vial',
                            'childs'        : [
                                                {
                                                    'title'         : 'Subscription Plan',
                                                    'menu_item'     : 'subscription_lan',
                                                    'end_point'     : 'payment_bp.enter_client_id',
                                                    'icon_class'    : 'fa-dot-circle',
                                                
                                                },
                                            ]
                            }

test_module_menu_config = {
                            'title'         : 'Test',
                            'menu_item'     : 'test',
                            'icon_class'    : 'fas fa-vial',
                            'childs'        : [
                                                {
                                                    'title'         : 'Bootstap Divider',
                                                    'menu_item'     : 'bootstrap_divider',
                                                    'end_point'     : 'test_bp.bootstrap_divider',
                                                    'icon_class'    : 'fa-dot-circle',
                                                    
                                                
                                                },
                                                {
                                                    'title'         : 'Bootstrap Breadcrumb',
                                                    'menu_item'     : 'bootstrap_breadcrumb',
                                                    'end_point'     : 'test_bp.bootstrap_breadcrumb',
                                                    'icon_class'    : 'fa-dot-circle',
                                                
                                                },
                                                {
                                                    'title'         : 'Loading Content',
                                                    'menu_item'     : 'loading_content',
                                                    'end_point'     : 'test_bp.loading_content',
                                                    'icon_class'    : 'fa-dot-circle',
                                                
                                                },
                                                {
                                                    'title'         : 'Input Element',
                                                    'menu_item'     : 'input_element',
                                                    'end_point'     : 'test_bp.input_element',
                                                    'icon_class'    : 'fa-dot-circle',
                                                
                                                },
                                                {
                                                    'title'         : 'Multi Tabs',
                                                    'menu_item'     : 'multi_tabs',
                                                    'end_point'     : 'test_bp.multi_tabs',
                                                    'icon_class'    : 'fa-dot-circle',
                                                
                                                },
                                                {
                                                    'title'         : 'Show Modal',
                                                    'menu_item'     : 'show_modal',
                                                    'end_point'     : 'test_bp.show_modal',
                                                    'icon_class'    : 'fa-dot-circle',
                                                
                                                },
                                                {
                                                    'title'         : 'jsPDF Print',
                                                    'menu_item'     : 'jspdf_print',
                                                    'end_point'     : 'test_bp.show_jspdfprint',
                                                    'icon_class'    : 'fa-dot-circle',
                                                
                                                },
                                                payment_module_menu_config
                                                
                                                
                                                ]
                            
                            }


