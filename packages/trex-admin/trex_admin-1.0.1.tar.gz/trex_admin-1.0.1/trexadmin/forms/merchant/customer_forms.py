'''
Created on 7 Dec 2020

@author: jacklok
'''
'''
Created on 21 Apr 2020

@author: jacklok
'''
from wtforms import StringField, PasswordField, validators, DateField
from trexlib.forms.base_forms import ValidationBaseForm
from trexlib.libs.wtforms import validators as custom_validator
from flask_babel import gettext
from datetime import date

class CustomerSearchForm(ValidationBaseForm):
    name                = StringField('Name', [
                                        validators.Optional(),
                                        validators.Length(min=3, max=300, message='Name length must be within 3 and 300 characters'),
                                        custom_validator.RequiredIfOtherFieldsValueIsEmpty(
                                                        ['mobile_phone', 'email', 'merchant_tagging', 'reference_code', 'merchant_reference_code', 'registered_date_start', 'registered_date_end'],
                                                        message=gettext("Either one input is required")),
                                        ]
                                        )
    email               = StringField('Email Address', [
                                        validators.Optional(),
                                        validators.Email("Please enter valid email address."),
                                        custom_validator.RequiredIfOtherFieldsValueIsEmpty(
                                                        ['name', 'mobile_phone', 'merchant_tagging', 'reference_code', 
                                                         'merchant_reference_code', 'registered_date_start', 'registered_date_end'],
                                                        message=gettext("Either one input is required")),
                                        
                                        ]
                                        )
    
    mobile_phone        = StringField('Mobile Phone', [
                                        validators.Optional(),
                                        custom_validator.RequiredIfOtherFieldsValueIsEmpty(
                                                        ['name', 'email', 'merchant_tagging', 'reference_code', 
                                                         'merchant_reference_code', 'registered_date_start', 'registered_date_end'],
                                                        message=gettext("Either one input is required")),
                                        
                                        ]
                                        )
    
    merchant_tagging    = StringField('Tagging', [
                                        validators.Optional(),
                                        custom_validator.RequiredIfOtherFieldsValueIsEmpty(
                                                        ['mobile_phone', 'email', 'name', 'reference_code', 
                                                         'merchant_reference_code', 'registered_date_start', 'registered_date_end'],
                                                        message=gettext("Either one input is required")),
                                        ]
                                        )
    
    reference_code                = StringField('Reference code', [
                                        validators.Optional(),
                                        custom_validator.RequiredIfOtherFieldsValueIsEmpty(
                                                        ['mobile_phone', 'email', 'name', 'merchant_reference_code', 
                                                         'merchant_tagging', 'registered_date_start', 'registered_date_end'],
                                                        message=gettext("Either one input is required")),
                                        validators.Length(max=16, message="Reference code length must not more than 16 characters")
                                        ]
                                        )
    
    merchant_reference_code       = StringField('Member code', [
                                        validators.Optional(),
                                        custom_validator.RequiredIfOtherFieldsValueIsEmpty(
                                                        ['mobile_phone', 'email', 'name', 'reference_code', 'merchant_tagging', 
                                                         'registered_date_start', 'registered_date_end'],
                                                        message=gettext("Either one input is required")),
                                        validators.Length(max=16, message="Member code length must not more than 16 characters")
                                        ]
                                        )
    
    registered_date_start         = DateField('Program Start Date', default=date.today, format='%d/%m/%Y',validators=[
                                        validators.Optional(),
                                        custom_validator.RequiredIfOtherFieldsValueIsEmpty(
                                                        ['mobile_phone', 'email', 'name', 'reference_code', 'merchant_tagging', 
                                                         'merchant_reference_code', 'registered_date_end'],
                                                        message=gettext("Either one input is required")),
                                        ]
                                        )
    
    registered_date_end         = DateField('Program Start Date', default=date.today, format='%d/%m/%Y',validators=[
                                        validators.Optional(),
                                        custom_validator.RequiredIfOtherFieldsValueIsEmpty(
                                                        ['mobile_phone', 'email', 'name', 'reference_code', 'merchant_tagging', 
                                                         'merchant_reference_code', 'registered_date_start'],
                                                        message=gettext("Either one input is required")),
                                        ]
                                        )

class CustomerDetailsForm(CustomerSearchForm):
    customer_key                = StringField('Customer Key')
    merchant_reference_code     = StringField('Member Code')
    gender                      = StringField('Gender', [
                                                #validators.DataRequired(message="Gender is required"),
                                        ])
    registered_outlet           = StringField('Registered Outlet')
    
class CustomerContactForm(ValidationBaseForm):
    user_key            = StringField('User Key')
    address             = StringField('Address', [
                                        validators.Length(max=1000, message="Address length must not more than 1000 characters")
                                        ])
    postcode            = StringField('Postcode', [
                                        validators.Length(max=10, message="Postcode length must not more than 10 characters")
                                        ])
    city                = StringField('City', [
                                        validators.Length(max=100, message="City length must not more than 100 characters")
                                        ]
                                        )
    state               = StringField('State', [
                                        validators.Length(max=100, message="Postcode length must not more than 100 characters")
                                        ])
    country             = StringField('Country', [
                                        validators.Length(max=100, message="Postcode length must not more than 100 characters")
                                        ])
    
class CustomerBiodataForm(ValidationBaseForm):
    user_key            = StringField('User Key')
    gender              = StringField('Gender')
    birth_date          = DateField('Date of Birth', format='%d/%m/%Y')    


class CustomerMembershipForm(ValidationBaseForm):    
    customer_key                = StringField('Customer Key')
    membership_key              = StringField(
                                    label='Membership',
                                    validators=[
                                        validators.DataRequired(message="Membership is required"),
                                        ] 
                                    )
    
    tier_membership_key         = StringField(
                                    label='Tier Membership', 
                                    )
    
    assigned_outlet             = StringField('Assign Outlet',[
                                                validators.DataRequired(message="Assign Outlet is required"),
                                            ])
    
class CustomerMemberKPIForm(ValidationBaseForm):    
    customer_key                = StringField('Customer Key')
    membership_key              = StringField(
                                    label='Membership', 
                                    
                                    )
    
    tier_membership_key         = StringField(
                                    label='Tier Membership', 
                                    )
    tags_list                   = StringField('Tag to Classify Member')
    
    
    
    
class CustomerRegistrationForm(CustomerDetailsForm):
    password            = PasswordField('Password', [
                                        validators.DataRequired(message="Password is required"),
                                        validators.EqualTo('confirm_password', message='Passwords must match')
                                        ]
                                        )
    confirm_password    = PasswordField('Confirm Password',[
                                        validators.DataRequired(message="Confirm password is required")
                                        ]
                                        )    
    registered_outlet   = StringField('Registered Outlet')

class ResetCustomerPasswordForm(ValidationBaseForm):
    key                 = StringField('Customer Key', [
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


class SignInForm(ValidationBaseForm):
    signin_email            = StringField('Signin Email', [
                                        validators.DataRequired(message="Email is required"),
                                        validators.Length(min=7, max=150, message="Emaill address length must be within 7 and 150 characters"),
                                        validators.Email("Please enter valid email address.")
                                        ]
                                        )
    password                = PasswordField('New Password', [
                                        validators.InputRequired()
                                        ]
                                        ) 
    

        
    
class ChangePasswordForm(ValidationBaseForm):
    existing_password       = PasswordField('Existing Password')
    new_password            = PasswordField('New Password', [
                                        validators.InputRequired(), 
                                        validators.EqualTo('confirm_password', message='New passwords must match')
                                        ]
                                        )
    confirm_password        = PasswordField('Repeat Password')    


