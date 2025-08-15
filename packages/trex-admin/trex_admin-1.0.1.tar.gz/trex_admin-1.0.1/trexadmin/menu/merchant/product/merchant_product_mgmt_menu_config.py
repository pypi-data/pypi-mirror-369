'''
Created on 22 Jul 2021

@author: jacklok
'''

from flask_babel import gettext


merchant_product_category_setup_menu_item = {
                                    'title'         : gettext('Category Setup'),
                                    'menu_item'     : 'merchant_product_category_setup',
                                    'end_point'     : 'product_category_setup_bp.product_category_setup',
                                    'icon_class'    : 'fas fa-plus-circle',
                                    'permission'    : 'merchant_product_category_setup',
                        
                        }

merchant_product_setup_menu_item = {
                                    'title'         : gettext('Product Setup'),
                                    'menu_item'     : 'merchant_product_mgmt',
                                    'end_point'     : 'product_setup_bp.product_search',
                                    'icon_class'    : 'fas fa-plus-circle',
                                    'permission'    : 'merchant_product_setup',
                        
                        }

merchant_product_option_setup_menu_item = {
                                    'title'         : gettext('Option Setup'),
                                    'menu_item'     : 'merchant_product_option_mgmt',
                                    'end_point'     : 'product_setup_bp.product_option_search',
                                    'icon_class'    : 'fas fa-plus-circle',
                                    'permission'    : 'merchant_product_option_setup',
                        
                        }

merchant_product_modifier_setup_menu_item = {
                                    'title'         : gettext('Modifier Setup'),
                                    'menu_item'     : 'merchant_product_modifier_setup',
                                    'end_point'     : 'product_modifier_setup_bp.product_modifier_listing',
                                    'icon_class'    : 'fas fa-plus-circle',
                                    'permission'    : 'merchant_product_modifier_setup',
                        
                        }

merchant_product_catalogue_setup_menu_item = {
                                    'title'         : gettext('Catalogue Setup'),
                                    'menu_item'     : 'merchant_product_catalogue_setup',
                                    'end_point'     : 'product_catalogue_setup_bp.product_catalogue_listing',
                                    'icon_class'    : 'fas fa-plus-circle',
                                    'permission'    : 'merchant_product_catalogue_setup',
                        
                        }


product_submenu_items = {
                                
                                'title'         : gettext('Product'),
                                'menu_item'     : 'merchant_product',
                                'icon_class'    : 'fas fa-cubes',
                                'permission'    : ['merchant_product_setup', 'merchant_product_modifier_setup', 'merchant_product_category_setup'],
                                #'product_code'  : ['loyalty','point_of_sales'],
                                #'product_code'  : 'loyalty',
                                'childs'        : [
                                    
                                                    merchant_product_modifier_setup_menu_item,
                                                    merchant_product_category_setup_menu_item,
                                                    merchant_product_setup_menu_item,
                                                    merchant_product_catalogue_setup_menu_item,
                                                            
                                                ]
                }