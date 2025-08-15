'''
Created on 15 May 2020

@author: jacklok
'''

from wtforms import StringField, PasswordField, validators, BooleanField, SelectField, SelectMultipleField
from wtforms.fields.html5 import DateField
from trexlib.forms.base_forms import ValidationBaseForm
from trexadmin.controllers.system.system_route_helpers import get_merchant_permission_list
from trexlib.libs.wtforms import validators as custom_validator
from trexlib.libs.wtforms import fields as custom_fields
from datetime import date
from flask_babel import gettext
from wtforms.fields.core import IntegerField, FloatField
 

class MerchantSignInForm(ValidationBaseForm):
    username            = StringField('SignIn username', [
                                        validators.DataRequired(message="SignIn username is required"),
                                        validators.Length(min=3, max=30, message='SignIn username length must be within 3 and 30 characters')
                                        ]
                                        )
    password                = PasswordField('Password', [
                                        validators.InputRequired()
                                        ]
                                        )
    redirect_url            = StringField('Redirect_url', [])

class MerchantSearchForm(ValidationBaseForm):
    company_name        = StringField('Company Name', [
                                        validators.Length(max=150, message='Company name length must be within 3 and 150 characters'),
                                        custom_validator.RequiredIfOtherFieldsValueIsEmpty(
                                                        ['account_code'],
                                                        message=gettext("Either one input is required")),
                                        ]
                                        )
    account_code        = StringField('Account Code', [
                                        validators.Length(max=19, message='Account code length must be within 19 characters'),
                                        custom_validator.RequiredIfOtherFieldsValueIsEmpty(
                                                        ['company_name'],
                                                        message=gettext("Either one input is required")),
                                        ]
                                        )
    
    
class MerchantDetailsForm(MerchantSearchForm):    
    key                 = StringField('Key')
    brand_name          = StringField('Brand Name', [
                                        validators.Length(max=150, message='Brand name length must be within 3 and 100 characters'),
                                        ]
                                        )
    business_reg_no     = StringField('Business Registration No', [
                                        validators.Length(min=0, max=30, message='Business Registration No length must be within 30 characters'),
                                        
                                    ])
    contact_name        = StringField('Contact Name', [
                                        validators.DataRequired(message="Contact name is required"),
                                        validators.Length(min=3, max=150, message='Contact name length must be within 3 and 150 characters')
                                        ]
                                        )
    mobile_phone        = StringField('Contact Mobile Phone', [
                                        ]
                                        )
    office_phone        = StringField('Contact Office Phone', [
                                        ]
                                        )
    
    website             = StringField('Website', [
                                        ]
                                        )
    
    email               = StringField('Email Address', [
                                        validators.DataRequired(message="Email is required"),
                                        validators.Length(min=7, max=150, message="Emaill address length must be within 7 and 150 characters"),
                                        validators.Email("Please enter valid email address.")
                                        ]
                                        )
    
    
class AddMerchantForm(MerchantDetailsForm):
    plan_start_date     = DateField('Plan Start Date',default=date.today, format='%d/%m/%Y')
    plan_end_date       = DateField('Plan End Date',default=date.today, format='%d/%m/%Y')
    currency_code       = StringField('Currency', [
                                                    validators.DataRequired(message="Currency is required"),
                                                    ])   
    country             = StringField('Country', [
                                                    validators.DataRequired(message="Country is required"),
                                        ]
                                        )
    
    industry             = StringField('Industry', [
                                                    validators.DataRequired(message="Industry is required"),
                                        ]
                                        )
    
    timezone            = StringField('Timezone', [
                                                    validators.DataRequired(message="Timezone is required"),
                                                    ])
    
    product_package     = StringField('Product Package', [
                                                    validators.DataRequired(message="Product Package is required"),
                                        ]
                                        )
    
    loyalty_package     = StringField('Loyalty Plan', [
                                                    validators.Optional(),
                                        ]
                                        )
    pos_package         = StringField('Point Of Sales Plan', [
                                                    validators.Optional(),
                                        ]
                                        )
    
    outlet_limit                = IntegerField(gettext('Outlet limit'),[
                                                #validators.InputRequired(message=gettext("Outlet limit is required")),
                                                
                                            ])

class MerchantUserForm(ValidationBaseForm):
    
    name                = StringField('Full name', [
                                        validators.DataRequired(message="Fullname is required"),
                                        validators.Length(min=3, max=150, message='Fullname length must be within 3 and 150 characters')
                                        ]
                                        )
    username            = StringField('SignIn username', [
                                        validators.DataRequired(message="SignIn username is required"),
                                        validators.Length(min=3, max=30, message='SignIn username length must be within 3 and 30 characters')
                                        ]
                                        )
    
class SearchMerchantUserForm(ValidationBaseForm):
    
    name                = StringField('Full name', [
                                        custom_validator.RequiredIfOtherFieldsValueIsEmpty(
                                                        ['username', 'assigned_outlet'],
                                                        message=gettext("Either one input is required")),
                                        validators.Length(min=0, max=150, message='Fullname length must be within 3 and 150 characters')
                                        ]
                                        )
    
    username            = StringField('SignIn username', [
                                        custom_validator.RequiredIfOtherFieldsValueIsEmpty(
                                                        ['assigned_outlet', 'name'],
                                                        message=gettext("Either one input is required")),
                                        validators.Length(min=0, max=30, message='SignIn username length must be within 3 and 30 characters')
                                        ]
                                        )    
    
    assigned_outlet       = StringField('Assign Outlet',[
                                        custom_validator.RequiredIfOtherFieldsValueIsEmpty(
                                                        ['username','name'],
                                                        message=gettext("Either one input is required")),
                                        
                                                
                                        ])  

class AddMerchantUserForm(MerchantUserForm): 
    merchant_acct_key   = StringField('Merchant Acct Key')
    password            = PasswordField('Password', [
                                        validators.DataRequired(message="Password is required"),
                                        validators.EqualTo('confirm_password', message='Passwords must match')
                                        ]
                                        )
    confirm_password    = PasswordField('Confirm Password',[
                                        validators.DataRequired(message="Confirm password is required")
                                        ]
                                        )
    

class UpdateMerchantUserForm(MerchantUserForm):
    merchant_user_key   = StringField('Merchant User Key', [
                                        ]
                                        )
    
class ResetMerchantUserPasswordForm(ValidationBaseForm):
    key                 = StringField('Merchant User Key', [
                                        ]
                                        )    
    
    password            = PasswordField('Password', [
                                        validators.DataRequired(message="Password is required"),
                                        validators.EqualTo('confirm_password', message='Passwords must match')
                                        ]
                                        )
    confirm_password    = PasswordField('Confirm Password',[
                                        validators.DataRequired(message="Confirm password is required")
                                        ]
                                        )             

class MerchantUserPermissionForm(ValidationBaseForm):
    merchant_user_key           = StringField('Merchant User Key', [
                                        validators.DataRequired(message="Merchant user key is required")
                                    ])
    merchant_acct_key           = StringField('Merchant Account Key', [])
    is_admin                    = BooleanField('Is administrator', [])
    access_permission           = SelectMultipleField(
                                    label='Access Permission', 
                                    validators=[
                                            custom_validator.RequiredIfOtherFieldValueIsFalse(
                                                        'is_admin',
                                                        message="Acccess Permission is required"),
                                    ],
                                    choices=get_merchant_permission_list(None)
                                    )
    
    outlet_permission           = custom_fields.NoPrevalidateSelectMultipleField(
                                    label='Outlet Permission', 
                                    validators=[
                                            custom_validator.RequiredIfOtherFieldValueIsFalse(
                                                        'is_admin',
                                                        message="Outlet Permission is required"),
                                    ]
                                    )
    
class SearchMerchantOutletForm(ValidationBaseForm):
    name                = StringField('Outlet name', [
                                        validators.DataRequired(message="Outlet name is required"),
                                        validators.Length(min=0, max=150, message='Outlet name length must be within 3 and 150 characters')
                                        ]
                                        )       
        
class MerchantOutletBaseForm(ValidationBaseForm):
    
    outlet_name                     = StringField('Outlet Name', [
                                        validators.DataRequired(message="Outlet name is required"),
                                        validators.Length(min=0, max=150, message='Outlet name length must be within 3 and 150 characters')
                                    ])
    
    outlet_id                       = StringField('Outlet Id', [
                                        validators.Length(min=0, max=5, message='Outlet id length must be within 5 characters'),
                                        validators.regexp('^[0-9]*$', message="Only numeric text"),
                                    ])
    
    company_name                    = StringField('Outlet Registered Company Name', [
                                        validators.Length(min=0, max=150, message='Outlet Registered Company Name No length must be within 150 characters'),
                                        
                                    ])
    
    business_reg_no                 = StringField('Business Registration No', [
                                        validators.Length(min=0, max=30, message='Business Registration No length must be within 30 characters'),
                                        
                                    ])
    
    business_hour                   = StringField('Business Hour', [])
    address                         = StringField('Address', [
                                        validators.Length(min=0, max=150, message='Outlet address length must be within 3 and 300 characters')
                                        ])
    geo_location                    = StringField('Geo location', [])
    office_phone                    = StringField('Office Phone no.', [])
    fax_phone                       = StringField('Fax Phone no.', [])
    email                           = StringField('Email', [])
    is_physical_store               = BooleanField('Is Physical Store')
    is_headquarter                  = BooleanField('Is Head Quarter',)

class AddMerchantOutletForm(MerchantOutletBaseForm):
    merchant_acct_key               = StringField('Merchant Account Key', [
                                        validators.DataRequired(message="Merchant account key is required")
                                    ])
class MerchantOutletDetailsForm(MerchantOutletBaseForm):
    merchant_outlet_key             = StringField('Merchant Outlet Key', [
                                        validators.DataRequired(message="Merchant outlet key is required")
                                    ])    

class AddMerchantTaggingForm(ValidationBaseForm):
    label                       = StringField('Tag label', [
                                        validators.DataRequired(message="Tag label is required")
                                    ])
    desc                        = StringField('Tag description', [])
    
class AddMerchantPromotionCodeForm(ValidationBaseForm):
    label                       = StringField('Code label', [
                                        validators.DataRequired(message="Code label is required")
                                    ])
    desc                        = StringField('Code description', [])    
    
class UpdateMerchantTaggingForm(AddMerchantTaggingForm):
    tag_key                        = StringField('Tag Key', [validators.DataRequired(message="Tag key is required")])    
    

class UpdateMerchantPromotionCodeForm(AddMerchantPromotionCodeForm):
    tag_code                        = StringField('Promotion Code', [validators.DataRequired(message="Promotion Code is required")])    

    
class ServiceTaxSetupForm(ValidationBaseForm):
    service_tax_setup_key                = StringField('Service Tax Setup Key')
    tax_reg_id                           = StringField('Tax Registration Id', [
                                                validators.DataRequired(message="Tax registration id is required"),
                                                validators.Length(min=0, max=30, message='Tax registration id length must be within 3 and 30 characters')
                                            ])
    tax_name                             = StringField('Tax Name', [
                                                validators.DataRequired(message="Tax Name is required"),
                                                validators.Length(min=0, max=150, message='Tax Name length must be within 3 and 150 characters')
                                            ])
    tax_label                            = StringField('Tax Label', [
                                                validators.DataRequired(message="Tax Label is required"),
                                                validators.Length(min=0, max=20, message='Tax Label length must be within 3 and 20 characters')
                                            ])
    tax_apply_type                       = StringField('Tax Apply Type', [
                                                validators.DataRequired(message="Tax apply type is required"),
                                                
                                            ])
    tax_pct_amount                       = FloatField(gettext('Tax percentage amount'),[
                                                validators.InputRequired(message=gettext("Charge percentage amount is required")),
                                                validators.NumberRange(min=0, max=100),
                                            ])
    assign_outlet                        = StringField('Assign Outlet',[
                                                validators.InputRequired(message=gettext("Assign Outlet is required")),
                                                
                                            ])     
    
class ProgramSettingsForm(ValidationBaseForm):    
    days_of_return_policy                    = IntegerField(gettext('No of day for return policy'),[
                                                validators.InputRequired(message=gettext("No of day for return policy is required")),
                                                
                                            ])
    days_of_repeat_purchase_measurement      = IntegerField(gettext('No of day for repeat purcase measurement'),[
                                                validators.InputRequired(message=gettext("No of day for repeat purcase measurement is required")),
                                                
                                            ])
    
    membership_renew_advance_day             = IntegerField(gettext('Number of advance day to renew membership'),[
                                                validators.InputRequired(message=gettext("Number of advance day to renew membership is required")),
                                                
                                            ])
    
    membership_renew_late_day               = IntegerField(gettext('Number of day late to renew membership'),[
                                                validators.InputRequired(message=gettext("Number of day late to renew membership is required")),
                                                
                                            ]) 
    rating_review                           = BooleanField('Rating Review',[])
    
            