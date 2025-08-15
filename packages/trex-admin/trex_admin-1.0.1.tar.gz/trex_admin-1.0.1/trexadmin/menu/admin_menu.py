'''
Created on 8 Jan 2021

@author: jacklok
'''

from trexadmin.menu import admin_setting_menu_config, admin_report_menu_config


dashboard_menu_item = {
                        'title'         : 'Dashboard',
                        'menu_item'     : 'admin_dashboard',
                        'end_point'     : 'admin_bp.dashboard_content',
                        'icon_class'    : 'fas fa-desktop',
                        'permission'    : '',
                        'active'        : True,
                }

menu_items  = [
                        dashboard_menu_item,
                        admin_report_menu_config.menu_items, 
                        admin_setting_menu_config.menu_items,
                        ]  
