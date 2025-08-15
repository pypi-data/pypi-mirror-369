'''
Created on 22 Dec 2020

@author: jacklok
'''
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

upload_file_sub_menu_config = {
                            'title'         : 'Upload File',
                            'menu_item'     : 'upload_file',
                            'icon_class'    : 'fas fa-upload',
                            'childs'        : [
                                                {
                                                    'title'         : 'Upload Single Image',
                                                    'menu_item'     : 'upload_single_image',
                                                    'end_point'     : 'test_upload_bp.upload_image',
                                                    'icon_class'    : 'fa-dot-circle',
                                                
                                                },
                                            ]
                            }

menu_items = {
                            'title'         : 'Test',
                            'menu_item'     : 'test',
                            'icon_class'    : 'fas fa-vial',
                            'childs'        : [
                                                {
                                                    'title'         : 'Firebase Counter',
                                                    'menu_item'     : 'firebase_counter',
                                                    'end_point'     : 'test_bp.show_firebase_counter',
                                                    'icon_class'    : 'fa-dot-circle',
                                                
                                                },
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
                                                {
                                                    'title'         : 'Stepper Linear',
                                                    'menu_item'     : 'stepper',
                                                    'end_point'     : 'test_bp.show_stepper_horizontal',
                                                    'icon_class'    : 'fa-dot-circle',
                                                
                                                },
                                                {
                                                    'title'         : 'Stepper Vertical',
                                                    'menu_item'     : 'stepper',
                                                    'end_point'     : 'test_bp.show_stepper_vertical',
                                                    'icon_class'    : 'fa-dot-circle',
                                                
                                                },
                                                {
                                                    'title'         : 'Treeview Menu 1',
                                                    'menu_item'     : 'stepper',
                                                    'end_point'     : 'test_bp.show_treeview_menu1',
                                                    'icon_class'    : 'fa-dot-circle',
                                                
                                                },
                                                {
                                                    'title'         : 'Treeview Menu 2',
                                                    'menu_item'     : 'stepper',
                                                    'end_point'     : 'test_bp.show_treeview_menu2',
                                                    'icon_class'    : 'fa-dot-circle',
                                                
                                                },
                                                {
                                                    'title'         : 'Send Email',
                                                    'menu_item'     : 'send_email',
                                                    'end_point'     : 'test_bp.send_email',
                                                    'icon_class'    : 'fa-dot-circle',
                                                
                                                },
                                                
                                                #payment_module_menu_config,
                                                upload_file_sub_menu_config,
                                                
                                                
                                                ]
                            
                            }