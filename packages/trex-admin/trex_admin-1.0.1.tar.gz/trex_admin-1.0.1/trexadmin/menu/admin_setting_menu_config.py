'''
Created on 17 Dec 2020

@author: jacklok
'''
manage_admin_sub_menu = {
                            'title'         : 'Manage Admin Account',
                            'menu_item'     : 'manage_admin',
                            'end_point'     : 'manage_admin_bp.manage_administrator',
                            'icon_class'    : 'fa-dot-circle',
                            'permission'    : 'manage_admin',
                        }

manage_merchant_sub_menu = {
                            'title'         : 'Manage Merchant Account',
                            'menu_item'     : 'manage_merchant',
                            'end_point'     : 'admin_manage_merchant_bp.manage_merchant',
                            'icon_class'    : 'fa-dot-circle',
                            'permission'    : 'manage_merchant',
                        }

manage_contact_us_sub_menu = {
                        'title'         : 'Manage Contact Us Listing',
                        'menu_item'     : 'manage_contact_us',
                        'end_point'     : 'manage_contact_us_bp.manage_contact_us_listing',
                        'icon_class'    : 'fa-dot-circle',
                        'permission'    : 'manage_contact_us',
                        }

upload_banner_sub_menu = {
                        'title'         : 'Upload Banner',
                        'menu_item'     : 'upload_banner',
                        'end_point'     : 'admin_manage_banner_bp.manage_banner_index',
                        'icon_class'    : 'fa-dot-circle',
                        'permission'    : 'upload_banner',
                        }

menu_items = {
                'title'         : 'Settings',
                'menu_item'     : 'settings',
                'icon_class'    : 'fas fa-cogs',
                'permission'    : ['manage_merchant', 'manage_user', 'manage_contact_us'],
                'childs'        : [
                                    manage_admin_sub_menu,
                                    manage_merchant_sub_menu,
                                    upload_banner_sub_menu,
                                    manage_contact_us_sub_menu,
                                    
                                            
                                ]
            } 

